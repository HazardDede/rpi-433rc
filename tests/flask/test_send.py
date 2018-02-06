import json


def test_send_code(flask_client, mocked_rfdevice):
    resp = flask_client.get('/send/12345', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    assert {'code': 12345, 'result': True} == json.loads(resp.data.decode("utf-8"))

    # mocked_rfdevice.enable_tx.assert_called()
    mocked_rfdevice.tx_code.assert_called_with(12345)
