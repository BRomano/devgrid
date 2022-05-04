from flask import Blueprint
from devgrid import cache
from devgrid.temperature import routes  # noqa: F401

temperature_bp = Blueprint('temperature', __name__)


@cache.memoize()
def _get_city_temperature(city_name: str):
    return None
