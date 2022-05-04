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
    (3, 'Dijon,Lyon,London', 'Lyon,London', 10), # expired one
    (3, 'Dijon,Lyon,London', 'London', 12), # expired 2
    (3, 'Dijon,Lyon,London', '', 14), # everything were expired
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


logs1 = [
    ["58523", "user_1", "resource_1"],
    ["62314", "user_2", "resource_2"],
    ["54001", "user_1", "resource_3"],
    ["200", "user_6", "resource_5"],
    ["215", "user_6", "resource_4"],
    ["54060", "user_2", "resource_3"],
    ["53760", "user_3", "resource_3"],
    ["58522", "user_22", "resource_1"],
    ["53651", "user_5", "resource_3"],
    ["2", "user_6", "resource_1"],
    ["100", "user_6", "resource_6"],
    ["400", "user_7", "resource_2"],
    ["100", "user_8", "resource_6"],
    [ "54359", "user_1", "resource_3"],
]


def time_calc(time, window):
    time_window = [time]
    for t in window:
        _diff = abs(time - t)
        print(f'{time} - {t} = {_diff}')
        if _diff != 0 and _diff <= 300:
            time_window.append(t)

    return time_window


def test_xxx():
    window_1 = {}
    window = []

    for log in logs1:
        if log[2] not in window_1:
            window_1[log[2]] = {'values': [int(log[0])]}
        else:
            window_1[log[2]].get('values').append(int(log[0]))

    for resource in window_1:
        for time in window_1[resource].get('values'):
            window.append({
                'resource': resource,
                'array': time_calc(time, window_1[resource].get('values'))})

    print(f'window = {window}')
    key_one = {'array': []}
    key_one_max_value = 0
    for r in window:
        max_value = max(len(r.get('array')), len(key_one.get('array')))
        if max_value > key_one_max_value:
            key_one_max_value = max_value
            key_one = r

    return key_one
