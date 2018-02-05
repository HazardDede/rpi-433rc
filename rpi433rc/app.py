from flask import Flask

app = Flask(__name__)

from .api.flaskutil.routing import OnOffConverter
app.url_map.converters['on_off'] = OnOffConverter

from .api import api
api.init_app(app)
