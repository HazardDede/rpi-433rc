import pytest

from rpi433rc.app import app
from rpi433rc.business.devices import StatefulDevice, CodeDevice, SystemDevice
import rpi433rc.business.rc433 as rc433
import rpi433rc.api as api


@pytest.yield_fixture(scope='session')
def flask_app():
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def flask_client(flask_app):
    # flask_app.response_class = utils.JSONResponse
    return flask_app.test_client()


@pytest.yield_fixture(scope='function')
def mocked_rfdevice(mocker):
    mocker.patch.object(rc433.RFDevice, 'enable_tx')
    mocker.patch.object(rc433.RFDevice, 'tx_code')
    mocker.patch.object(rc433.RFDevice, 'cleanup')
    rc433.RFDevice.enable_tx.return_value = None
    rc433.RFDevice.tx_code.return_value = True
    rc433.RFDevice.cleanup.return_value = None

    yield rc433.RFDevice


@pytest.yield_fixture(scope='function')
def mocked_device_db(mocker):
    mocker.patch.object(api.device_db, 'list')
    mocker.patch.object(api.device_db, 'lookup')
    mocker.patch.object(api.device_db, 'switch')

    api.device_db.list.return_value = [
        StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False),
        StatefulDevice(device=CodeDevice('device2', code_on=12345, code_off=23456), state=True),
        StatefulDevice(device=SystemDevice('device3', system_code="00001", device_code=4), state=True),
    ]
    api.device_db.lookup.return_value = StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False)
    api.device_db.switch.return_value = None

    yield api.device_db