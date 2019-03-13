import re
from abc import abstractmethod
from collections import defaultdict
from threading import Thread

import attr

from .devices import Device
from .util import LogMixin


@attr.s
class DeviceState(LogMixin):
    """
    Abstract base class for a device state tracker.
    """
    def _device_name(self, device_or_name):
        if isinstance(device_or_name, Device):
            return device_or_name.device_name

        return device_or_name

    @abstractmethod
    def lookup(self, device_or_name):
        """
        Lookup the state of a single device by the specified name or entity.

        Args:
            device_or_name: A real device entity (Device) or it's name

        Returns:
            Returns True if the device is currently on; otherwise False.
        """
        pass

    @abstractmethod
    def switch(self, device_or_name, on):
        """
        Switch on / off the specified device.

        Args:
            device_or_name: A real device entity (Device) or it's name
            on: If True the device will be marked as on; otherwise off.

        Returns:
            None
        """
        pass


@attr.s
class MemoryState(DeviceState):
    """
    In-memory implementation of a device state mapping.

    Example:

        >>> dut = MemoryState()
        >>> dut.lookup(Device('device1'))
        False

        >>> dut.switch(Device('device2'), True)
        >>> dut.lookup(Device('device1')), dut.lookup(Device('device2'))
        (False, True)
    """

    def __attrs_post_init__(self):
        self.states = defaultdict(bool)

    def lookup(self, device_or_name):
        """
        Lookup the state of a single device by the specified name or entity.

        Args:
            device_or_name: A real device entity (Device) or it's name

        Returns:
            Returns True if the device is currently on; otherwise False.
        """
        return self.states.get(self._device_name(device_or_name), False)

    def switch(self, device_or_name, on):
        """
        Switch on / off the specified device.

        Args:
            device_or_name: A real device entity (Device) or it's name
            on: If True the device will be marked as on; otherwise off.

        Returns:
            None
        """
        self.states[self._device_name(device_or_name)] = on


@attr.s
class MQTTState(MemoryState):
    class _StateListener(LogMixin):
        def __init__(self, host, port, user, password, state_callback, topic_fun):
            self.host = str(host)
            self.port = int(port)
            self.user = user
            self.password = password
            # Callback to report state for device (args: device_name, state as bool)
            self.state_callback = state_callback
            # Transformation function to alter the placeholder device_name of the topic
            # Used for regex extraction and subscribing
            self.topic_fun = topic_fun
            self._client = None

        def _on_connect(self, client, userdata, flags, rc):
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            if rc == 0:
                client.subscribe(self.topic_fun('+'))  # Subscribe to all device topics
                self.logger.info("Connected with result code '{rc}' "
                                 "to {self.topic} @ {self.host}:{self.port}".format(**locals()))
            else:
                self.logger.error("Bad connection with result code '{rc}' "
                                  "to {self.topic} @ {self.host}:{self.port}".format(**locals()))

        def _on_disconnect(self, client, userdata, rc):
            if rc != 0:
                self.logger.warning("Unexpected mqtt disconnect with result code '{rc}'. "
                                    "Will automatically reconnect.".format(**locals()))

        def _on_message(self, client, obj, msg):
            topic = msg.topic
            message = msg.payload.decode('utf-8')
            self.logger.info("Got message from broker on topic '{topic}'. "
                             "Payload='{message}'".format(**locals()))

            pattern = self.topic_fun(r'(\w+)')  # Replace device_name by pattern to extract
            m = re.match(pattern, topic)
            if m:
                device_name = m.group(1)
                self.state_callback(device_name, message == 'on')
            else:
                self.logger.warning("Could not extract device_name from '{topic}'".format(**locals()))

        def run(self):
            import paho.mqtt.client as paho
            self._client = paho.Client()
            if self.user:
                self._client.username_pw_set(self.user, self.password)
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.on_disconnect = self._on_disconnect
            self._client.connect(self.host, self.port, 60)
            self._client.loop_forever()

        def run_async(self):
            t = Thread(target=self.run)
            t.daemon = True
            t.start()

    host = attr.ib(converter=str)
    port = attr.ib(converter=int, default=1883)
    user = attr.ib(converter=str, default=None)
    password = attr.ib(converter=str, default=None)
    topic_pattern = attr.ib(converter=str, default='rc433/{device_name}/switch')

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.state_listener = self._StateListener(
            self.host,
            self.port,
            self.user,
            self.password,
            state_callback=super().switch,
            topic_fun=self._make_topic
        )
        self.state_listener.run_async()

    def _publish(self, on_off, topic, qos):
        import paho.mqtt.publish as publish

        auth = None
        if self.user is not None:
            auth = dict(username=self.user, password=self.password)

        payload = on_off
        if isinstance(payload, bool):
            payload = 'on' if on_off else 'off'

        publish.single(
            topic=topic,
            payload=payload,
            hostname=self.host,
            port=self.port,
            retain=True,
            auth=auth,
            qos=qos
        )
        self.logger.info("Published rc433 state '{payload}' on '{topic}' @ {self.host}:{self.port} with qos={qos}."
                         .format(**locals()))

    def _make_topic(self, device_name):
        return self.topic_pattern.format(device_name=device_name)

    def switch(self, device_or_name, on):
        device_name = self._device_name(device_or_name)
        real_topic = self._make_topic(device_name)

        try:
            self._publish(on, real_topic, qos=0)
        except Exception:
            import traceback
            error = traceback.format_exc()
            self.logger.error("Error when publishing state '{on}' for device '{device_name}' on mqtt:\n"
                              "{error}".format(**locals()))
