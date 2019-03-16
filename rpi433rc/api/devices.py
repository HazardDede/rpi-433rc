"""Device related routes."""

from flask_restplus import Resource, Namespace, fields

from .flaskutil import fields as _fields
from .flaskutil.auth import requires_auth
from ..business.devices import UnknownDeviceError
from ..business.rc433 import UnsupportedDeviceError

api = Namespace('devices', description='Socket device related operations')  # pylint: disable=invalid-name


@api.errorhandler(UnknownDeviceError)
@api.errorhandler(UnsupportedDeviceError)
def unknown_device(error):
    """Unknown device error serializer."""
    return {'message': str(error), 'value': 'device_name'}, 400


STATE = api.model('State', {
    'state': _fields.OnOff,
    'result': fields.Boolean
})

DEVICE = api.model('Device', {
    'device_name': fields.String(attribute="device.device_name"),
    'type': fields.String(attribute=lambda o: (str(o.device.__class__.__name__)
                                               if hasattr(o, 'device') else None)),
    'configuration': _fields.Dict(attribute="device.configuration"),
    'state': _fields.OnOff
})


@api.route('/')
@api.route('/list')
class DeviceList(Resource):
    """Endpoint to list devices."""
    @requires_auth
    @api.marshal_with(DEVICE)
    def get(self):  # pylint: disable=no-self-use
        """Implements get operation."""
        from . import device_db
        devices = device_db.list()
        return devices


@api.route('/<string:device_name>')
class DeviceLookup(Resource):
    """Endpoint to lookup a specific device."""
    @requires_auth
    @api.marshal_with(DEVICE)
    def get(self, device_name):  # pylint: disable=no-self-use
        """Implements get operation."""
        from . import device_db
        return device_db.lookup(device_name=device_name)


@api.route('/<string:device_name>/<on_off:on_off>')
class DeviceSwitch(Resource):
    """Endpoint to switch a specific device to a given state."""
    @requires_auth
    @api.marshal_with(STATE)
    def get(self, device_name, on_off):  # pylint: disable=no-self-use
        """Implements get operation."""
        from . import device_db

        res = device_db.switch(on_off, device_name=device_name)
        return {'state': on_off, 'result': res}
