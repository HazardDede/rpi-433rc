"""Provides basic authentication stuff for flask."""

from functools import wraps

from flask import request, Response


def validate_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    from ...config import AUTH_USER, AUTH_PW
    return username == AUTH_USER and password == AUTH_PW


def auth_401():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(fun):
    """Decorator to mark endpoints that they require authentication."""
    @wraps(fun)
    def decorated(*args, **kwargs):
        from ...config import AUTH_USER
        if AUTH_USER is not None:
            auth = request.authorization
            if not auth or not validate_auth(auth.username, auth.password):
                return auth_401()
        return fun(*args, **kwargs)
    return decorated
