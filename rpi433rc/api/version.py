from flask_restplus import Resource, Namespace
from ..config import VERSION

api = Namespace('version', description='Version')


@api.route('/')
class Version(Resource):
    def get(self):
        return {'version': VERSION}
