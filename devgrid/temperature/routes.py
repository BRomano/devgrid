from flask import request, jsonify, current_app as app

from devgrid.temperature import temperature_bp as bp

from datetime import datetime
from pytz import timezone, utc
from collections import namedtuple


@bp.route('/<string:city_name>', methods=['GET'])
def get_city_temperature(city_name):
    """
    Will list all stores
    ---
    description: Will list all stores aggregated by sum(value)
    responses:
      200:
        description: An array of objects with all stores with SUM aggregation by value.
    """

    return jsonify({
        'city': city_name
    }), 200


@bp.route('', methods=['GET'])
def fetch_history():
    """
    Will route to cnab home
    ---
    description: Will fetch all transaction from a giving store_id
    parameters:
      - name: max_number
        in: query
        type: number
        description: retrieve cities history

    responses:
      200:
        description: A list of transactions.
      400:
        description: If could not find store.
    """

    max_number = request.args.get('max', app.config.DEFAULT_MAX_NUMBER)
    return jsonify({
        max: max_number
    }), 200
