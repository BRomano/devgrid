from flask import request, jsonify, current_app as app
from devgrid.temperature import temperature_bp as bp

from devgrid import cache
from devgrid.models import TemperatureEntry
import requests
from datetime import datetime
import pycountry


@cache.memoize(timeout=0)
def _get_country_code_alpha(alpha_2: str) -> str:
    _country_code_alpha_2 = alpha_2
    _country = pycountry.countries.get(alpha_2=_country_code_alpha_2)
    return _country.alpha_3


def _get_city_data_from_api(city_name: str) -> dict:
    """
    Always fetch from API

    :param city_name: city name
    :return: a TemperatureEntry dict object
    """
    weather_query = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={app.config["OPEN_WEATHER_MAP_KEY"]}&units=metric'
    response = requests.get(weather_query)
    if response.status_code != 200:
        raise Exception(response.json().get('message'))

    api_data = response.json()
    _entry = TemperatureEntry()
    _entry.min = api_data.get('main', {}).get('temp_min')
    _entry.max = api_data.get('main', {}).get('temp_max')
    _entry.avg = api_data.get('main', {}).get('temp')
    _entry.feels_like = api_data.get('main', {}).get('feels_like')
    _entry.city_name = city_name

    _data_api_sys = api_data.get('sys', {})
    if 'country' not in _data_api_sys:
        raise Exception('sys is not on return data api')

    _entry.city_country = _get_country_code_alpha(_data_api_sys.get('country'))
    _entry.requested_at = datetime.utcnow()
    return _entry.to_primitive()


def _fetch_city_data(city_name: str) -> dict:
    """
    This function will get the object from cache if there is no cached information, it will fetch from API

    :param city_name: City Name
    :return: a TemperatureEntry dict object
    """
    # store the cache key
    is_data_cached = cache.cache.has(city_name)
    _city_data = None
    if is_data_cached:
        _city_data = cache.cache.get(city_name)
    else:
        _city_data = _get_city_data_from_api(city_name)
        cache.cache.set(city_name, _city_data)

    _city_data['cached_data'] = is_data_cached

    cities_index = set()
    if cache.cache.has('cities_index'):
        cities_index = cache.get('cities_index')

    cities_index.add(city_name)
    # timeout 0 to never expire
    cache.cache.set('cities_index', cities_index, 0)

    return _city_data


@bp.route('/<string:city_name>', methods=['GET'])
def get_city_temperature(city_name):
    """
    Will retrieve city's weather from API and store data on cache
    ---
    description: Will retrieve city's weather API on cache for configured time, or 300 seconds by default
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
      ErrorMessage:
        type: object
        properties:
          message:
            type: string
    responses:
      200:
        description: The object retrieved from thrid party API, or getted from cache. If Attribute cached_data is false, the object was cached
        schema:
          $ref: '#definitions/TemperatureEntry'
      400:
        description: if any error occur on endpoint
        schema:
          $ref: '#definitions/ErrorMessage'
    """

    try:
        _city_data = _fetch_city_data(city_name)
        return jsonify(_city_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@bp.route('', methods=['GET'])
def fetch_history():
    """
    Will retrive from cache maximum cities based on max query parameter
    ---
    description: Will fetch from cache limited to a max items
    parameters:
      - name: max
        in: query
        type: number
        description: retrieve cities history

    responses:
      200:
        description: A list of city's weather retriveved from store.
        schema:
          type: array
          items:
            $ref: '#definitions/TemperatureEntry'
      500:
        description: If any error occur on endpoint
        schema:
          $ref: '#definitions/ErrorMessage'
    """

    try:
        max_number = int(request.args.get('max', app.config.get('DEFAULT_MAX_NUMBER')))
        cities_index: set = cache.cache.get('cities_index')
        if cities_index is None:
            cities_index = set()

        cached_cities = []
        for city_name in cities_index:
            if max_number < 1:
                break

            is_cached = cache.cache.has(city_name)
            if is_cached:
                cached_cities.append(city_name)
                max_number -= 1

        city_dict = {}
        if len(cached_cities) > 0:
            city_dict = cache.cache.get_dict(*cached_cities)

        return jsonify(list(city_dict.values())), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
