"""Provides version related endpoints."""

from flask_restplus import Resource, Namespace

api = Namespace('version', description='Version')  # pylint: disable=invalid-name


@api.route('/')
class Version(Resource):
    """Endpoint that provides the current version of the api."""
    def get(self):  # pylint: disable=no-self-use
        """Implements get operation."""
        from ..config import VERSION
        return {'version': VERSION}
