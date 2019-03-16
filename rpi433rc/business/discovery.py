"""MQTT discovery related components."""

import attr

from .registry import DeviceRegistry
from ..model import MQTTConfig, MQTTTopicConfig
from ..util import MQTTListener, LogMixin, on_off_to_bool, MQTTPublisher, safe_call


class Callback(LogMixin):
    """Callback for incoming mqtt messages on the command topic(s)."""
    def __init__(self, registry, topic_config):
        self.topic_config = topic_config
        self.registry = registry

    @safe_call
    def on_mqtt_message(self, topic, message):
        """Is called when an actual mqtt message arrives."""
        device_name = self.topic_config.extract_device_from_topic(topic, pattern='command')
        if not device_name:
            self.logger.warning("Could not extract device_name from '%s'", topic)
            return
        self.registry.switch(on_off=on_off_to_bool(message), device_name=device_name)


@attr.s
class MQTTDiscovery(LogMixin):
    """Publishes mqtt discovery compliant confugrations and listens for
    state-change requests on the command topics of all devices."""
    mqtt_config = attr.ib(validator=attr.validators.instance_of(MQTTConfig))
    topic_config = attr.ib(validator=attr.validators.instance_of(MQTTTopicConfig))
    registry = attr.ib(validator=attr.validators.instance_of(DeviceRegistry))

    def _start_command_listener(self, async_mode):
        command_topic_str = self.topic_config.mk_all_commands_topic()
        callback = Callback(self.registry, self.topic_config)
        listener = MQTTListener(
            config=self.mqtt_config,
            listen_topic=command_topic_str,
            message_callback=callback.on_mqtt_message
        )
        if async_mode:
            listener.run_async()
        else:
            listener.run()

    def _publish_config(self):
        publisher = MQTTPublisher(self.mqtt_config)
        for dev in self.registry.list():
            self.logger.debug("Publishing discovery config for %s", dev.device_name)
            config_topic = self.topic_config.mk_config_topic(dev.device_name)
            config = {
                'command_topic': self.topic_config.mk_command_topic(dev.device_name),
                'name': dev.device_name,
                'state_on': 'on',
                'state_off': 'off',
                'payload_on': 'on',
                'payload_off': 'off'
            }
            publisher.publish(config, config_topic, qos=0)

    def run(self, async_mode=False):
        """Runs the discovery component. Whether async (non-blocking; threaded)
        or sync (blocking)."""
        if not self.mqtt_config.is_valid():
            raise RuntimeError("MQTT Config is not valid")
        if not self.topic_config.supports_commands():
            raise RuntimeError("MQTT Topic configuration does not support commands")

        self._publish_config()
        self._start_command_listener(async_mode)
