"""A place for utility functions, decorators, classes..."""

import functools
import json
import logging
from threading import Thread

import attr

from .model import MQTTConfig


def on_off_to_bool(str_):
    """
    Converts a str that should represent on/off to a boolean

    Example:
        >>> on_off_to_bool('on'), on_off_to_bool('off')
        (True, False)
        >>> on_off_to_bool('ON'), on_off_to_bool('OFF')
        (True, False)

    """
    str_ = str(str_)
    if str_.lower() in ['on', 'true', 'an']:
        return True
    return False


def bool_to_on_off(bool_):
    """Converts a boolean to on/off

    Example:
        >>> bool_to_on_off(True)
        'on'
        >>> bool_to_on_off(False)
        'off'
    """
    bool_ = bool(bool_)
    return 'on' if bool_ else 'off'


def safe_call(fun):
    """
    Catches any exception that the decorated function/method raises, logs it (logging module)
    and simply returns None.
    Args:
        fun: The function to decorate.

    Returns:
        If no exception is raised the return value of the wrapped function;
        otherwise None (+ side effect of logging).

    Example:

        >>> @safe_call
        ... def fail_by_design():
        ...     raise RuntimeError("Oh, no!!!")

        >>> print(fail_by_design())
        None

    """
    @functools.wraps(fun)
    def _wrap(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception:  # pylint: disable=broad-except
            import traceback
            logging.error(traceback.format_exc())
        return None
    return _wrap


class LogMixin:  # pylint: disable=too-few-public-methods
    """
    Provides a logger property to any class where this class is mixed-in.

    Example:

        >>> class Dummy(LogMixin):
        ...     def do_something_fancy(self):
        ...         self.logger.info("Begin")
        ...         # ...
        ...         self.logger.info("End")
    """
    @property
    def logger(self):
        """Returns the configured logging instance."""
        return logging.getLogger(self.__class__.__name__)


@attr.s
class MQTTPublisher(LogMixin):
    """
    Utility class to publish to a mqtt broker.
    """
    config = attr.ib(validator=attr.validators.instance_of(MQTTConfig))

    @staticmethod
    def _qos(qos):
        qos = int(qos)
        if qos > 3:
            qos = 3
        if qos < 0:
            qos = 0
        return qos

    def publish(self, payload, topic, retain=True, qos=0):
        """
        Does the actual publishing of the given payload to the specified topic.

        Args:
            payload: Payload to publish.
            topic: The topic to use.
            retain: If True, the published message will be "sticky"
            qos: Quality of service.

        Returns:
            None.
        """
        import paho.mqtt.publish as publish
        retain = bool(retain)
        qos = self._qos(qos)

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        auth = None
        if self.config.user is not None:
            auth = dict(username=self.config.user, password=self.config.password)

        publish.single(
            topic=topic,
            payload=payload,
            hostname=self.config.host,
            port=self.config.port,
            retain=retain,
            auth=auth,
            qos=qos
        )
        self.logger.info("Published '%s' on '%s' @ %s:%s with qos=%s.",
                         payload, topic, self.config.host, self.config.port, qos)


@attr.s
class MQTTListener(LogMixin):
    """Utlity class to listen to one or many (wildcards) topics on a mqtt broker."""
    config = attr.ib(validator=attr.validators.instance_of(MQTTConfig))
    listen_topic = attr.ib(converter=str)
    message_callback = attr.ib(validator=lambda inst, attr, value: callable(value))
    _client = attr.ib(default=None, init=False)

    def _on_connect(self, client, userdata, flags, rc):  # pylint: disable=invalid-name,unused-argument
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        topic = self.listen_topic
        if rc == 0:
            # Subscribe to all device related state topics
            client.subscribe(topic)  # Subscribe to all device topics
            self.logger.info("Connected with result code '%s' to %s @ %s:%s",
                             rc, topic, self.config.host, self.config.port)
        else:
            self.logger.error("Bad connection with result code '%s' to %s @ %s:%s",
                              rc, topic, self.config.host, self.config.port)

    def _on_disconnect(self, client, userdata, rc):  # pylint: disable=invalid-name,unused-argument
        if rc != 0:
            self.logger.warning("Unexpected mqtt disconnect with result code '%s'. "
                                "Will automatically reconnect.", rc)

    @safe_call
    def _on_message(self, client, obj, msg):  # pylint: disable=unused-argument
        topic = msg.topic
        message = msg.payload.decode('utf-8')
        self.logger.info("Got message from broker on topic '%s'. Payload='%s'",
                         topic, message)
        self.message_callback(topic, message)

    def run(self):
        """
        Runs the listener in a blocking manner.
        Returns:
            None.
        """
        import paho.mqtt.client as paho
        self._client = paho.Client()
        if self.config.user:
            self._client.username_pw_set(self.config.user, self.config.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect
        self._client.connect(self.config.host, self.config.port, 60)
        try:
            self._client.loop_forever()
        except KeyboardInterrupt:
            pass

    def run_async(self):
        """
        Runs the listener in a non-blocking manner (async).
        Returns:
            None.
        """
        thr = Thread(target=self.run)
        thr.daemon = True
        thr.start()
