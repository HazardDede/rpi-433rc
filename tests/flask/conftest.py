import pytest

from rpi433rc.app import app


@pytest.yield_fixture(scope='session')
def flask_app():
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def flask_client(flask_app):
    # flask_app.response_class = utils.JSONResponse
    return flask_app.test_client()
