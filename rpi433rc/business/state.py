"""Device state related components."""
from abc import abstractmethod

import attr

from .devices import device_validator
from ..model import MQTTConfig, MQTTTopicConfig
from ..util import (MQTTPublisher, safe_call, LogMixin, MQTTListener, on_off_to_bool,
                    bool_to_on_off)


@attr.s
class DeviceState(LogMixin):
    """
    Abstract base class for a device state tracker.
    """
    def init_device(self, device):  # pylint: disable=unused-argument,no-self-use
        """The registry will call this method to initialize all known devices."""
        return

    def init_done(self):  # pylint: disable=no-self-use
        """The registry will call this method, when the initialization is done."""
        return

    @abstractmethod
    def lookup(self, device=None, device_name=None):
        """
        Lookup the state of a single device by the specified name or entity.

        Args:
            device: A real device entity (Device)
            device_name: ... or it's name

        Returns:
            Returns True if the device is currently on; otherwise False.
        """
        raise NotImplementedError()

    @abstractmethod
    def switch(self, on_off, device=None, device_name=None):
        """
        Switch on / off the specified device.

        Args:
            device: A real device entity (Device)
            device_name: ... or it's name
            on_off: If True the device will be marked as on; otherwise off.

        Returns:
            None
        """
        raise NotImplementedError()


@attr.s
class MemoryState(DeviceState):
    """
    In-memory implementation of a device state mapping.

    Example:
        >>> from rpi433rc.business.devices import Device
        >>> dut = MemoryState()
        >>> dut.lookup(device=Device('device1'))
        False

        >>> dut.switch(True, device=Device('device2'))
        >>> dut.lookup(device=Device('device1')), dut.lookup(device_name='device2')
        (False, True)
    """

    states = attr.ib(default=None, repr=True, cmp=False, hash=False, init=False)

    def __attrs_post_init__(self):
        if self.states is None:
            self.states = dict()

    def init_device(self, device):
        """The registry will call this method to initialize all known devices."""
        self.states[device.device_name] = False

    @device_validator
    def lookup(self, device=None, device_name=None):
        return self.states.get(device_name, False)

    @device_validator
    def switch(self, on_off, device=None, device_name=None):
        self.logger.debug("Switching %s to %s", str(device_name), str(on_off))
        self.states[device_name] = on_off


@attr.s
class MQTTState(MemoryState):
    """MQTT state tracker implementation. Gets and publishes the state to a mqtt broker."""

    config = attr.ib(validator=attr.validators.instance_of(MQTTConfig))
    topic = attr.ib(validator=attr.validators.instance_of(MQTTTopicConfig))
    state_listener = attr.ib(default=None, repr=False, cmp=False, hash=False, init=False)

    def init_done(self):
        self.state_listener = MQTTListener(
            config=self.config,
            listen_topic=self.topic.mk_all_states_topic(),
            message_callback=self._on_state_message
        )
        self.state_listener.run_async()

    @safe_call
    def _on_state_message(self, topic, message):
        """Callback to process any state related messages from the mqtt listener"""
        device_name = self.topic.extract_device_from_topic(topic)
        if device_name is None:
            self.logger.warning("Could not extract device_name from '%s'", topic)
            return
        super().switch(on_off_to_bool(message), device_name=device_name)

    @device_validator
    def switch(self, on_off, device=None, device_name=None):
        real_topic = self.topic.mk_state_topic(device_name)

        payload = on_off
        if isinstance(payload, bool):
            payload = bool_to_on_off(payload)

        try:
            MQTTPublisher(self.config).publish(payload, real_topic, qos=0)
        except Exception:  # pylint: disable=broad-except
            import traceback
            error = traceback.format_exc()
            self.logger.error("Error when publishing state '%s' for device '%s' on mqtt:\n"
                              "%s", on_off, device_name, error)
