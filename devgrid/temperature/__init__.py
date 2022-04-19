from flask import Blueprint
from devgrid import cache
temperature_bp = Blueprint('temperature', __name__)

from devgrid.temperature import routes

@cache.memoize()
def _get_city_temperature(city_name: str):
    return None
