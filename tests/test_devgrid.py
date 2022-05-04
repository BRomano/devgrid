import pytest
import time


@pytest.mark.parametrize("city_name, status_code, country", [
    ('Curitiba', 200, 'BRA'),
    ('London', 200, 'GBR'),
    ('New York', 200, 'USA'),
    ('Montevideo', 200, 'URY'),
    ('Santiago', 200, 'CHL'),
    ('Talcahuano', 200, 'CHL'),
    ('Cuiaba', 200, 'BRA'),
    ('Santarem', 200, 'BRA'),
    ('Omaha', 200, 'USA'),
    ('Omahax', 400, ''),
    ('OmahaY', 400, ''),
])
def test_get_city_country(client, city_name, status_code, country):
    res = client.get(f'/temperature/{city_name}')
    json_data = res.get_json()
    if 'message' in json_data:
        print(json_data.get('message'))
    assert res.status_code == status_code
    if res.status_code == 200:
        assert json_data.get('city_name') == city_name
        assert json_data.get('city_country') == country
        assert json_data.get('cached_data') is False


@pytest.mark.parametrize("city_name, times, cached", [
    ('Carballo', 2, True),
    ('Bilbao', 1, False),
    ('Lyon', 3, True),
    ('Dijon', 1, False),
])
def test_get_cached_city(client, city_name, times, cached):
    for i in range(times):
        res = client.get(f'/temperature/{city_name}')
        assert res.status_code == 200
        if i > 0: # first iteration
            json_data = res.get_json()
            assert json_data.get('cached_data') is cached


@pytest.mark.parametrize("max_number, cities", [
    (0, 'Carballo,Curitiba,London,Omaha,Santiago,Montevideo'),
    (0, 'Carballo,Curitiba,London,Santiago'),
    (3, 'Bilbao,London'),
    (2, 'Lyon,Curitiba,London'),
    (1, 'Dijon'),
])
def test_get_cached_max(client, max_number, cities):
    #To build cache
    for city_name in cities.split(','):
        res = client.get(f'/temperature/{city_name}')
        assert res.status_code == 200
        json_data = res.get_json()
        assert json_data.get('cached_data') is False

    fetch_number = max_number
    url = f'/temperature?max={max_number}'
    if max_number == 0:
        url = f'/temperature'
        fetch_number = 5 #default value

    res = client.get(url)
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data) <= fetch_number
    for obj in json_data:
        assert obj.get('city_name') in cities


@pytest.mark.parametrize("max_number, cities, not_expired_cities, sleep_to_expire", [
    (3, 'Dijon,Lyon,London', 'Dijon,Lyon,London', 1), # SHould retrieve everything
    (3, 'Dijon,Lyon,London', 'Lyon,London', 11), # expired one
    (3, 'Dijon,Lyon,London', 'London', 13), # expired 2
    (3, 'Dijon,Lyon,London', '', 15), # everything were expired
    (5, 'Carballo,Curitiba,London,Omaha,Santiago,Montevideo','London,Omaha,Santiago,Montevideo', 4),
])
def test_get_cached_expire(client, max_number, cities, not_expired_cities, sleep_to_expire):
    #To build cache
    for city_name in cities.split(','):
        city_name = city_name.strip()
        res = client.get(f'/temperature/{city_name}')
        assert res.status_code == 200
        json_data = res.get_json()
        assert json_data.get('cached_data') is False
        time.sleep(2)

    time.sleep(sleep_to_expire)
    res = client.get(f'/temperature?max={max_number}')
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data) <= max_number

    # all retrieve cities on endpoint should be not expired
    for obj in json_data:
        assert obj.get('city_name') in not_expired_cities

    # not expired cities should be retrieved by endpoint
    if len(not_expired_cities) > 0:
        returned_cities = [o.get('city_name') for o in json_data]
        for city in not_expired_cities.split(','):
            assert city in returned_cities
