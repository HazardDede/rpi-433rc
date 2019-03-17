"""Configuration defaults and overrides by environment vars"""

import os

# Version
VERSION = '1.1.0'

# General
CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(os.path.dirname(__file__), '../conf'))
PORT = 5000  # Do not change OR change the ./run.sh as well
DEBUG = bool(os.environ.get('DEBUG', False))

# RC433 device
GPIO_OUT = int(os.environ.get('GPIO_OUT', 17))

# Authentication
# Basic Auth is disabled by default. Set the AUTH_USER envvar to enable it
AUTH_USER = os.environ.get('AUTH_USER', None)
AUTH_PW = os.environ.get('AUTH_PW', '12345')

# MQTT support
MQTT_HOST = os.environ.get('MQTT_HOST', None)
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USER = os.environ.get('MQTT_USER', None)
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', None)
MQTT_ROOT = os.environ.get('MQTT_ROOT', 'rc433')
MQTT_STATE_TOPIC = os.environ.get('MQTT_STATE_TOPIC', 'state')
MQTT_DISCOVERY = bool(os.environ.get('MQTT_DISCOVERY', False))
MQTT_COMMAND_TOPIC = os.environ.get('MQTT_COMMAND_TOPIC', 'set')
