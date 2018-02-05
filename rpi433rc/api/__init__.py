from flask_restplus import Api

from ..business.devices import DeviceDict, MemoryState, DeviceRegistry
from ..business.rc433 import RC433
from ..config import VERSION, GPIO_OUT

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


device_dict = {
    'device1': {"code_on": 12345, 'code_off': "23456"},
    'device2': {"system_code": "00010", "device_code": "2"}
}
device_db = DeviceRegistry(DeviceDict(device_dict), MemoryState())

rc433 = RC433(gpio_out=GPIO_OUT)
