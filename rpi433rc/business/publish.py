from abc import abstractmethod

import attr
from .util import LogMixin


def from_config():
    from ..config import MQTT_HOST
    if MQTT_HOST is not None:
        return MQTTPublisher.from_config()
    return DummyPublisher.from_config()


@attr.s
class Publisher(LogMixin):
    @classmethod
    @abstractmethod
    def from_config(cls):
        raise NotImplementedError()

    @abstractmethod
    def publish(self, device_name, state):
        raise NotImplementedError()


class DummyPublisher(Publisher):
    @classmethod
    def from_config(cls):
        return cls()

    def publish(self, device_name, state):
        return


@attr.s
class MQTTPublisher(Publisher):
    host = attr.ib(converter=str)
    port = attr.ib(converter=int, default=1883)
    user = attr.ib(converter=str, default=None)
    password = attr.ib(converter=str, default=None)
    topic_pattern = attr.ib(converter=str, default='rc433/{device_name}')

    @classmethod
    def from_config(cls):
        from ..config import MQTT_HOST, MQTT_PASSWORD, MQTT_PORT, MQTT_TOPIC, MQTT_USER
        return cls(host=MQTT_HOST, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, topic_pattern=MQTT_TOPIC)

    def _publish(self, auth, qos, payload, retain, topic):
        import paho.mqtt.publish as publish

        publish.single(
            topic=topic,
            payload=payload,
            hostname=self.host,
            port=self.port,
            retain=retain,
            auth=auth,
            qos=qos
        )
        self.logger.info("Published rc433 state '{payload}' on '{topic}' @ {self.host}:{self.port} with qos={qos}."
                         .format(**locals()))

    def _make_topic(self, device_name):
        return self.topic_pattern.format(device_name=device_name)

    def publish(self, device_name, state):
        real_topic = self._make_topic(device_name)
        auth = None
        if self.user is not None:
            auth = dict(username=self.user, password=self.password)
        try:
            self._publish(auth, qos=0, payload='on' if state else 'off', retain=True, topic=real_topic)
        except Exception:
            import traceback
            error = traceback.format_exc()
            self.logger.error("Error when publishing state '{state}' for device '{device_name}' on mqtt:\n"
                              "{error}".format(**locals()))
