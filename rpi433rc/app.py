import logging

from flask import Flask

from .config import DEBUG

level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

app = Flask(__name__)

from .api.flaskutil.routing import OnOffConverter
app.url_map.converters['on_off'] = OnOffConverter

from .api import api
api.init_app(app)
