import base64

import pytest


@pytest.mark.parametrize('path, auth_code, non_auth_code', [
    ('/devices/list', 200, 401),
    ('/devices/device1', 200, 401),
    ('/devices/device1/on', 200, 401),
    ('/send/12345', 200, 401),
    ('/version/', 200, 200)
])
def test_send_code_with_auth(path, auth_code, non_auth_code, flask_client_with_auth, mocked_rfdevice, mocked_device_db):
    resp = flask_client_with_auth.get(path, headers={
        'Accept': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(b'admin:12345').decode('ascii')
    })
    assert resp.status_code == auth_code

    resp = flask_client_with_auth.get(path, headers={
        'Accept': 'application/json'
    })
    assert resp.status_code == non_auth_code
