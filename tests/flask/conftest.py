import pytest

from rpi433rc.app import app
from rpi433rc.business.devices import StatefulDevice, CodeDevice, SystemDevice
from rpi433rc.business.rc433 import RFDevice
from rpi433rc.api import device_db


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
    mocker.patch.object(RFDevice, 'enable_tx')
    mocker.patch.object(RFDevice, 'tx_code')
    mocker.patch.object(RFDevice, 'cleanup')
    RFDevice.enable_tx.return_value = None
    RFDevice.tx_code.return_value = True
    RFDevice.cleanup.return_value = None

    yield RFDevice


@pytest.yield_fixture(scope='function')
def mocked_device_db(mocker):
    mocker.patch.object(device_db, 'list')
    mocker.patch.object(device_db, 'lookup')
    mocker.patch.object(device_db, 'switch')

    device_db.list.return_value = [
        StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False),
        StatefulDevice(device=CodeDevice('device2', code_on=12345, code_off=23456), state=True),
        StatefulDevice(device=SystemDevice('device3', system_code="00001", device_code=4), state=True),
    ]
    device_db.lookup.return_value = StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False)
    device_db.switch.return_value = None

    yield device_db