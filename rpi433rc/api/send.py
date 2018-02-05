from flask_restplus import Resource, Namespace, fields

api = Namespace('send', description='Remote control related operations')


code = api.model('Code', {
    'code': fields.Integer,
    'result': fields.Boolean
})


@api.route('/<int:code>')
class SendCode(Resource):
    @api.marshal_with(code)
    def get(self, code):
        from . import rc433
        return {'code': code, 'result': rc433.send_code(code)}
