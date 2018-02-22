import os

from flask_restplus import Api

from ..business.devices import DeviceDict, MemoryState, DeviceRegistry
from ..business.rc433 import RC433

from ..config import VERSION
api = Api(
    title='RPi433',
    version=VERSION,
    description='Raspberry Pi 433mhz socket remote control Rest-API'
)

from .version import api as ns_version
api.add_namespace(ns_version)

from .devices import api as ns_devices
api.add_namespace(ns_devices)

from .send import api as ns_send
api.add_namespace(ns_send)

from ..config import GPIO_OUT, CONFIG_DIR
config_file = os.path.join(CONFIG_DIR, 'devices.json')
device_store = DeviceDict.from_json(config_file)
device_state = MemoryState()
device_db = DeviceRegistry(device_store, device_state)

rc433 = RC433(gpio_out=GPIO_OUT)
