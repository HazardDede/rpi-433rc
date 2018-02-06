import os

GPIO_OUT = int(os.environ.get('GPIO_OUT', 17))
CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(os.path.dirname(__file__), '../conf'))
DEBUG = bool(os.environ.get('DEBUG', False))

VERSION = '1.0.0'
