import pytest


def test_get_city(client):
    res = client.get('/temperature/Curitiba')
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data) > 0
