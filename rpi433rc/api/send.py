from flask_restplus import Resource, Namespace, fields

from .flaskutil.auth import requires_auth

api = Namespace('send', description='Remote control related operations')


code = api.model('Code', {
    'code': fields.Integer,
    'result': fields.Boolean
})


@api.route('/<int:code>')
class SendCode(Resource):
    @requires_auth
    @api.marshal_with(code)
    def get(self, code):
        from . import rc433
        return {'code': code, 'result': rc433.send_code(code)}
