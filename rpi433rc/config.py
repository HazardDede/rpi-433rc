import os

GPIO_OUT = int(os.environ.get('GPIO_OUT', 17))
CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(os.path.dirname(__file__), '../conf'))
DEBUG = bool(os.environ.get('DEBUG', False))

# Basic Auth is disabled by default. Set the AUTH_USER envvar to enable it
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PW = os.environ.get('AUTH_PW', '12345')

VERSION = '1.0.0'
