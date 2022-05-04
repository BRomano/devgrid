from flask import Blueprint
from devgrid import cache

temperature_bp = Blueprint('temperature', __name__)
from devgrid.temperature import routes  # noqa: E402,F401


@cache.memoize()
def _get_city_temperature(city_name: str):
    return None
