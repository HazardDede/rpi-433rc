import json


def test_version(flask_client):
    from rpi433rc.config import VERSION
    resp = flask_client.get('/version/', headers={'Accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'
    assert {"version": VERSION} == json.loads(resp.data.decode("utf-8"))

