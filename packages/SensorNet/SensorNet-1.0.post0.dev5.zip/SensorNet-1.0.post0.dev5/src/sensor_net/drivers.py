"""Defines drivers protocols."""
import typing

from .types import SensorData


class BackendDriver(typing.Protocol):
    """Basic backend driver."""

    def write(
            self,
            network_name: str,
            network_prefix: str,
            sensor_address: str,
            datas: typing.Iterable[SensorData],
    ) -> int:
        """
        Writes datas to the backend.

        :param network_name: Network name, not used
        :param network_prefix: Network prefix, not used
        :param sensor_address: Sensor address, not used
        :param datas: Sensor data, stored in the stub backend writes
        :raise BackendWriteError: if writes fails.
        """
        ...


get_driver: typing.TypeAlias = typing.Callable[[str, dict], BackendDriver]


class SensorDriver(typing.Protocol):
    """Basic sensor driver."""

    def read(self, url: str) -> typing.Iterable[SensorData]:
        """
        Reads sensor data from the driver.

        :param url: Sensor complete URL "http://host:port/api_location
        :return: Collection of sensor data.
        :raise APIReadError: if reads fails.
        """
        ...


get_sensor_driver: typing.TypeAlias = typing.Callable[[str, dict], SensorDriver]
