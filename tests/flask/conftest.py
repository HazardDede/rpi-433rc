import pytest


@pytest.fixture(scope='function')
def flask_client():
    from rpi433rc.app import app
    import rpi433rc.config as cfg
    cfg.AUTH_USER = None

    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='function')
def flask_client_with_auth():
    from rpi433rc.app import app
    import rpi433rc.config as cfg
    cfg.AUTH_USER = "admin"
    cfg.AUTH_PW = "12345"

    with app.app_context():
        yield app.test_client()


@pytest.yield_fixture(scope='function')
def mocked_rfdevice(mocker):

    import rpi433rc.business.rc433 as rc433
    mocker.patch.object(rc433.RFDevice, 'enable_tx')
    mocker.patch.object(rc433.RFDevice, 'tx_code')
    mocker.patch.object(rc433.RFDevice, 'cleanup')
    rc433.RFDevice.enable_tx.return_value = None
    rc433.RFDevice.tx_code.return_value = True
    rc433.RFDevice.cleanup.return_value = None

    yield rc433.RFDevice


@pytest.yield_fixture(scope='function')
def mocked_device_db(mocker):
    import rpi433rc.api as api
    mocker.patch.object(api.device_db, 'list')
    mocker.patch.object(api.device_db, 'lookup')
    mocker.patch.object(api.device_db, 'switch')

    from rpi433rc.business.devices import StatefulDevice, CodeDevice, SystemDevice
    api.device_db.list.return_value = [
        StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False),
        StatefulDevice(device=CodeDevice('device2', code_on=12345, code_off=23456), state=True),
        StatefulDevice(device=SystemDevice('device3', system_code="00001", device_code=4), state=True),
    ]
    api.device_db.lookup.return_value = StatefulDevice(device=CodeDevice('device1', code_on=12345, code_off=23456), state=False)
    api.device_db.switch.return_value = None

    yield api.device_db


@pytest.yield_fixture(scope='function')
def mocked_publisher(mocker):
    import rpi433rc.api as api
    mocker.patch.object(api.publisher, 'publish')

    yield api.publisher
