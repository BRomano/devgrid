from flask import request, jsonify, current_app as app
from devgrid.temperature import temperature_bp as bp

from devgrid import cache
from devgrid.models import TemperatureEntry
import requests


@cache.memoize()
def _get_city_data(city_name: str) -> dict:
    weather_query = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={app.config["OPEN_WEATHER_MAP_KEY"]}'
    response = requests.get(weather_query)
    if response.status_code != 200:
        raise Exception('Request error')

    api_data = response.json()
    _entry = TemperatureEntry()
    _entry.min = api_data.get('main', {}).get('temp_min')
    _entry.max = api_data.get('main', {}).get('temp_max')
    _entry.avg = api_data.get('main', {}).get('temp')
    _entry.feels_like = api_data.get('main', {}).get('feels_like')
    _entry.city_name = city_name
    _entry.city_country = api_data.get('sys', {}).get('country')
    return _entry.to_primitive()


@bp.route('/<string:city_name>', methods=['GET'])
def get_city_temperature(city_name):
    """
    Will retrieve weather API and store city values on cache
    ---
    description: Will retrieve weather API and store city values on cache for configured time, or 300 seconds
    parameters:
      - name: city_name
        in: path
        type: string
        required: true
        description: The city name to query weather data
    definitions:
      TemperatureEntry:
        type: object
        properties:
          city_name:
            type: string
          city_country:
            type: string
          feels_like:
            type: number
          avg:
            type: number
          max:
            type: number
          min:
            type: number
          requested_at:
            type: string
            format: date
          cached_data:
            type: boolean
    responses:
      200:
        description: An array of objects with all stores with SUM aggregation by value.
        schema:
          $ref: '#definitions/TemperatureEntry'
    """

    cache_key = _get_city_data.make_cache_key(_get_city_data, city_name)
    cached_data = cache.cache.has(cache_key)
    _city_data = _get_city_data(city_name)
    _city_data['cached_data'] = cached_data

    cities_index = set()
    if cache.cache.has('cities_index'):
        cities_index = cache.get('cities_index')

    cities_index.add(city_name)
    # timeout 0 to never expire
    cache.cache.set('cities_index', cities_index, 0)
    return jsonify(_city_data), 200


@bp.route('', methods=['GET'])
def fetch_history():
    """
    Will route to cnab home
    ---
    description: Will fetch all transaction from a giving store_id
    parameters:
      - name: max
        in: query
        type: number
        description: retrieve cities history

    responses:
      200:
        description: A list of transactions.
        schema:
          $ref: '#definitions/TemperatureEntry'
      400:
        description: If could not find store.
    """

    max_number = int(request.args.get('max', app.config.get('DEFAULT_MAX_NUMBER')))

    cities_index: set = cache.cache.get('cities_index')
    if cities_index is None:
        cities_index = set()

    cached_cities = []
    for _i_city in cities_index:
        if max_number < 1:
            break

        city_key = _get_city_data.make_cache_key(_get_city_data, _i_city)
        is_cached = cache.cache.has(city_key)
        if is_cached:
            cached_cities.append(city_key)
            max_number-=1

    city_dict = {}
    if len(cached_cities) > 0:
        city_dict = cache.cache.get_dict(*cached_cities)

    return jsonify(list(city_dict.values())), 200
