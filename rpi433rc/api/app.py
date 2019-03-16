"""Initializes the flask app."""
# pylint: skip-file

from flask import Flask

app = Flask(__name__)

from .flaskutil.routing import OnOffConverter
app.url_map.converters['on_off'] = OnOffConverter

from . import api
api.init_app(app)
