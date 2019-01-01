import attr
from .util import LogMixin
from ..config import MQTT_HOST, MQTT_PASSWORD, MQTT_PORT, MQTT_TOPIC, MQTT_USER


def from_config():
    if MQTT_HOST is not None:
        return MQTTPublisher.from_config()
    return DummyPublisher.from_config()


@attr.s
class Publisher(LogMixin):
    @classmethod
    def from_config(cls):
        raise NotImplementedError()

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
    topic = attr.ib(converter=str, default='rc433')

    @classmethod
    def from_config(cls):
        return cls(host=MQTT_HOST, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, topic=MQTT_TOPIC)

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
        self.logger.debug("Published rc433 state '{payload}' on '{topic}' @ {self.host}:{self.port} with qos={qos}."
                          .format(**locals()))

    def _make_topic(self, device_name):
        return self.topic + device_name if self.topic.endswith('/') else self.topic + '/' + device_name

    def publish(self, device_name, state):
        real_topic = self._make_topic(device_name)
        auth = None
        if self.user is not None:
            auth = dict(username=self.user, password=self.password)
        self._publish(auth, 1, 'on' if state else 'off', True, real_topic)
