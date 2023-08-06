"""Defines exported types."""
import collections
import datetime

SensorData = collections.namedtuple('SensorData', ["name", "value", "datetime_utc"])


def sensor_data_guard(sensor_data: SensorData):
    """
    Ensures that the sensor data is matching the expected types.

    :param sensor_data: Data to check
    :raise TypeError: if the attribute does not have the expected types
    """
    for t, v in zip([str, float, datetime.datetime], sensor_data):
        if not isinstance(v, t):
            raise TypeError("Invalid SensorData, expected (str, float, datetime).")
