from flask_restplus import Resource, Namespace

api = Namespace('version', description='Version')


@api.route('/')
class Version(Resource):
    def get(self):
        from ..config import VERSION
        return {'version': VERSION}
