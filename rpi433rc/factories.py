import functools
import logging


def log(entity_type):
    def wraps(fun):
        @functools.wraps(fun)
        def _call(*args, **kwargs):
            res = fun(*args, **kwargs)
            logging.info("Created {entity_type}: {res}".format(
                entity_type=entity_type,
                res=res
            ))
            return res
        return _call
    return wraps


@log("store")
def create_store():
    import os
    from .config import CONFIG_DIR
    from .business.devices import DeviceDict
    config_file = os.path.join(CONFIG_DIR, 'devices.json')
    store = DeviceDict.from_json(config_file)
    logging.info("Created store: {store}".format(**locals()))
    return store


@log("state")
def create_state():
    from .config import MQTT_HOST
    if MQTT_HOST is not None:
        from .business.state import MQTTState
        from .config import MQTT_PORT, MQTT_PASSWORD, MQTT_TOPIC, MQTT_USER
        return MQTTState(
            host=MQTT_HOST,
            port=MQTT_PORT,
            password=MQTT_PASSWORD,
            topic_pattern=MQTT_TOPIC,
            user=MQTT_USER
        )
    from .business.state import MemoryState
    return MemoryState()


@log("registry")
def create_registry():
    from .business.registry import DeviceRegistry
    device_store = create_store()
    device_state = create_state()
    rc433 = create_rc433()
    return DeviceRegistry(device_store, device_state, rc433)


@log("rc433")
def create_rc433():
    from .config import GPIO_OUT
    from .business.rc433 import RC433
    return RC433(gpio_out=GPIO_OUT)
