"""Factory utility function to create service classes."""

import functools
import logging


def log(entity_type):
    """Decorator to log output of method"""
    def wraps(fun):
        @functools.wraps(fun)
        def _call(*args, **kwargs):
            res = fun(*args, **kwargs)
            logging.info("Created %s: %s", str(entity_type), str(res))
            return res
        return _call
    return wraps


@log("store")
def create_store():
    """Create a device store based on your configuration"""
    import os
    from .config import CONFIG_DIR
    from .business.devices import DeviceDict
    config_file = os.path.join(CONFIG_DIR, 'devices.json')
    store = DeviceDict.from_json(config_file)
    return store


@log("state")
def create_state():
    """Create a device state service based on your configuration"""
    from .config import MQTT_HOST
    if MQTT_HOST is not None:
        from .business.state import MQTTState
        from .model import make_mqtt_config, make_mqtt_topic_config
        return MQTTState(
            config=make_mqtt_config(),
            topic=make_mqtt_topic_config()
        )
    from .business.state import MemoryState
    return MemoryState()


@log("registry")
def create_registry():
    """Create a device registry based on your configuration"""
    from .business.registry import DeviceRegistry
    device_store = create_store()
    device_state = create_state()
    rc433 = create_rc433()
    return DeviceRegistry(device_store, device_state, rc433)


@log("rc433")
def create_rc433():
    """Create a 433mhz controller based on your configuration"""
    from .config import GPIO_OUT
    from .business.rc433 import RC433
    return RC433(gpio_out=GPIO_OUT)


@log("mqtt_discovery")
def create_mqtt_discovery():
    """Create a mqtt discovery component based on your configuration"""
    from .model import make_mqtt_config, make_mqtt_topic_config
    mqtt_config = make_mqtt_config()
    topic_config = make_mqtt_topic_config()
    if not mqtt_config.is_valid() or not topic_config.supports_commands():
        return None  # Disable mqtt discovery
    from .business.discovery import MQTTDiscovery
    registry = create_registry()
    return MQTTDiscovery(mqtt_config=mqtt_config, topic_config=topic_config, registry=registry)
