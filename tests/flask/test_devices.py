import json


def test_list(flask_client, mocked_device_db):
    resp = flask_client.get('/devices/list', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    assert [{
        "device_name": "device1",
        "type": "CodeDevice",
        "configuration": {
            "code_on": 12345,
            "code_off": 23456
        },
        "state": "off"
    }, {
        "device_name": "device2",
        "type": "CodeDevice",
        "configuration": {
            "code_on": 12345,
            "code_off": 23456
        },
        "state": "on"
    }, {
        "device_name": "device3",
        "type": "SystemDevice",
        "configuration": {
            "system_code": "00001",
            "device_code": 4
        },
        "state": "on"
    }] == json.loads(resp.data)

    mocked_device_db.list.assert_called_once()


def test_lookup(flask_client, mocked_device_db):
    resp = flask_client.get('/devices/device1', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    assert {
        "device_name": "device1",
        "type": "CodeDevice",
        "configuration": {
            "code_on": 12345,
            "code_off": 23456
        },
        "state": "off"
    } == json.loads(resp.data)

    mocked_device_db.lookup.assert_called_with("device1")


def test_switch_on(flask_client, mocked_device_db, mocked_rfdevice):
    resp = flask_client.get('/devices/device1/on', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'

    assert {"state": "on", "result": True} == json.loads(resp.data)

    mocked_device_db.switch.assert_called()


def test_switch_off(flask_client, mocked_device_db, mocked_rfdevice):
    resp = flask_client.get('/devices/device1/off', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'

    assert {"state": "off", "result": True} == json.loads(resp.data)

    mocked_device_db.switch.assert_called()
