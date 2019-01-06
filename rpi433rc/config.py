import os

# Version
VERSION = '1.0.1'

# General
GPIO_OUT = int(os.environ.get('GPIO_OUT', 17))
CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(os.path.dirname(__file__), '../conf'))
DEBUG = bool(os.environ.get('DEBUG', False))

# Authentication
# Basic Auth is disabled by default. Set the AUTH_USER envvar to enable it
AUTH_USER = os.environ.get('AUTH_USER')
AUTH_PW = os.environ.get('AUTH_PW', '12345')

# MQTT support
MQTT_HOST = os.environ.get('MQTT_HOST', None)
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USER = os.environ.get('MQTT_USER', None)
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', None)
MQTT_TOPIC = os.environ.get('MQTT_TOPIC', 'rc433/{device_name}/switch')
