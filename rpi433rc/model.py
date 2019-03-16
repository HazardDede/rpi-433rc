"""Some heavily used models (by now only mqtt stuff)"""

import os
import re

import attr


def make_mqtt_config():
    """Returns a `MQTTCnfig` based on the user's configuration."""
    return MQTTConfig.from_config()


def make_mqtt_topic_config():
    """Returns a `MQTTTopicConfig` based on the user's configuration."""
    return MQTTTopicConfig.from_config()


@attr.s
class MQTTConfig:
    """Configuration to configure a mqtt client"""
    host = attr.ib(converter=str)
    port = attr.ib(converter=int, default=1883)
    user = attr.ib(converter=str, default=None)
    password = attr.ib(converter=str, default=None)

    def is_valid(self):
        """Checks if this configuration is valid"""
        return self.host != 'None'

    @classmethod
    def from_config(cls):
        """Load an instance from the actual configuration"""
        from .config import MQTT_PASSWORD, MQTT_PORT, MQTT_USER, MQTT_HOST
        return cls(host=MQTT_HOST, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)


@attr.s
class MQTTTopicConfig:
    """Utility class to handle mqtt topics and formatting."""
    discovery = attr.ib(converter=bool, default=False)
    root_topic = attr.ib(converter=str, default='rc433')
    state_topic = attr.ib(converter=str, default='state')
    command_topic = attr.ib(converter=str, default=None)

    def _root(self):
        root = self.root_topic
        if self.discovery:
            root = os.path.join(root, 'switch')
        return root

    def mk_state_topic(self, device_name):
        """Returns the state topic for the given device_name."""
        root = self._root()
        topic = os.path.join(root, "{device_name}", self.state_topic)
        return topic.format(device_name=device_name)

    def mk_all_states_topic(self):
        """Returns a pattern to listen on all state topics (for all devices)."""
        return self.mk_state_topic('+')

    def supports_commands(self):
        """Returns True if the topic configuration supports command topics, too."""
        return self.discovery and self.command_topic is not None

    def mk_command_topic(self, device_name):
        """Returns the command topic for the given device."""
        if not self.supports_commands():
            raise TypeError("No command topic is configured")
        root = self._root()
        topic = os.path.join(root, "{device_name}", self.command_topic)
        return topic.format(device_name=device_name)

    def mk_all_commands_topic(self):
        """Returns a pattern to listen on all command topics (for all devices)."""
        return self.mk_command_topic('+')

    def mk_config_topic(self, device_name):
        """Returns the configuration topic for the given device."""
        root = self._root()
        topic = os.path.join(root, "{device_name}", "config")
        return topic.format(device_name=device_name)

    def extract_device_from_topic(self, topic, pattern='state'):
        """Extracts the device name from a given topic string."""
        if pattern == 'command':
            pattern = self.mk_command_topic(r'(\w+)')  # Replace device_name by pattern to extract
        else:
            pattern = self.mk_state_topic(r'(\w+)')  # Replace device_name by pattern to extract
        match = re.match(pattern, topic)
        if match:
            try:
                return match.group(1)
            except IndexError:
                # No such group
                pass
        return None

    @classmethod
    def from_config(cls):
        """Loads an instance of `MQTTTopicConfig` from the actual configuration."""
        from .config import MQTT_DISCOVERY, MQTT_STATE_TOPIC
        if MQTT_DISCOVERY:
            from .config import MQTT_ROOT, MQTT_COMMAND_TOPIC
            return cls(
                discovery=MQTT_DISCOVERY,
                root_topic=MQTT_ROOT,
                state_topic=MQTT_STATE_TOPIC,
                command_topic=MQTT_COMMAND_TOPIC
            )

        return cls(
            discovery=MQTT_DISCOVERY,
            state_topic=MQTT_STATE_TOPIC
        )
