from schematics.models import Model
from schematics.types import StringType, DateTimeType, DecimalType, BooleanType

from datetime import datetime


class TemperatureEntry(Model):
    min = StringType(required=True)
    max = DecimalType(required=True)
    avg = DecimalType(required=True)
    feels_like = DecimalType(required=True)
    city_name = StringType(required=True)
    city_country = StringType(required=True)
    requested_at = DateTimeType(default=datetime.utcnow())
    cached_data = BooleanType(default=False)
