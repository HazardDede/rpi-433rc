"""Provides endpoints to send bare codes to devices via 433 mhz hardware."""

from flask_restplus import Resource, Namespace, fields

from .flaskutil.auth import requires_auth

api = Namespace('send', description='Remote control related operations')  # pylint: disable=invalid-name


CODE = api.model('Code', {
    'code': fields.Integer,
    'result': fields.Boolean
})


@api.route('/<int:code>')
class SendCode(Resource):
    """Endpoint to send bare 433mhz codes to devices in range."""
    @requires_auth
    @api.marshal_with(CODE)
    def get(self, code):  # pylint: disable=no-self-use
        """Implements get operation."""
        from . import device_db
        return {'code': code, 'result': device_db.rc433.send_code(code)}
