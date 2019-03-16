"""Main entrypoint to run the webserver and the mqtt discovery component."""

import logging

from gunicorn.app.base import Application

from rpi433rc.config import DEBUG
from rpi433rc.factories import create_mqtt_discovery


LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LEVEL)


def run_discovery(async_mode=False):
    """Runs the discovery component. Whether threaded (async) or non-threaded (sync and blocking)"""
    discovery = create_mqtt_discovery()
    if discovery:
        discovery.run(async_mode)
    else:
        logging.warning("MQTT Discovery mode disabled."
                        " Enable by `export MQTT_DISCOVERY=1`"
                        " AND `MQTT_HOST=<mqtt_host>`")


def run_server():
    """Runs the gunicorn backed webserver."""
    class WSGIServer(Application):
        """Wrapper around flask app to make it gunicorn compatible."""
        def init(self, parser, opts, args):
            pass

        def load(self):
            from rpi433rc.api.app import app
            return app

    WSGIServer().run()


def main():
    """Main entry point."""
    run_discovery(async_mode=True)
    run_server()


if __name__ == '__main__':
    main()
