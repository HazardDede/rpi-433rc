from flask_restplus import Resource, Namespace, fields

from .flaskutil import fields as _fields
from .flaskutil.auth import requires_auth
from ..business.devices import UnknownDeviceError
from ..business.rc433 import UnsupportedDeviceError

api = Namespace('devices', description='Socket device related operations')


@api.errorhandler(UnknownDeviceError)
@api.errorhandler(UnsupportedDeviceError)
def unknown_device(error):
    return {'message': str(error), 'value': 'device_name'}, 400


state = api.model('State', {
    'state': _fields.OnOff,
    'result': fields.Boolean
})

device = api.model('Device', {
    'device_name': fields.String(attribute="device.device_name"),
    'type': fields.String(attribute=lambda o: str(o.device.__class__.__name__) if hasattr(o, 'device') else None),
    'configuration': _fields.Dict(attribute="device.configuration"),
    'state': _fields.OnOff
})


@api.route('/')
@api.route('/list')
class DeviceList(Resource):
    @requires_auth
    @api.marshal_with(device)
    def get(self):
        from . import device_db
        devices = device_db.list()
        return devices


@api.route('/<string:device_name>')
class DeviceLookup(Resource):
    @requires_auth
    @api.marshal_with(device)
    def get(self, device_name):
        from . import device_db
        return device_db.lookup(device_name)


@api.route('/<string:device_name>/<on_off:on_off>')
class DeviceSwitch(Resource):
    @requires_auth
    @api.marshal_with(state)
    def get(self, device_name, on_off):
        from . import device_db
        from . import rc433
        device = device_db.lookup(device_name)
        res = rc433.switch_device(device, on_off)
        if res:
            # Mark the device as on resp. off
            device_db.switch(device_name, on_off)
        return {'state': on_off, 'result': res}
