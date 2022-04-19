import pytest


@pytest.mark.parametrize("city_name", [
    ('Curitiba'),
    ('Curitiba'),
    ('London'),
    ('New York'),
    ('New York'),
    ('Montevideo'),
    ('Santiago'),
    ('Talcahuano'),
    ('Cuiaba'),
    ('Santarem'),
    ('Omaha'),
])
def test_get_city(client, city_name):
    res = client.get(f'/temperature/{city_name}')
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data) > 0
