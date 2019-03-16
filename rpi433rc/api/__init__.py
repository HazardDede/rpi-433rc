"""Initializes the flask namespaces."""
# pylint: skip-file

from flask_restplus import Api

from ..config import VERSION

# pylint: disable=invalid-name
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

from ..factories import create_registry
device_db = create_registry()
