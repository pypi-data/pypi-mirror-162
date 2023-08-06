"""Base HTTP client implementation"""
import datetime
import json
import logging
import typing

import urllib3
import urllib3.exceptions

import sensor_net
from sensor_net.errors import (SensorDataTypeError, SensorNoResponseError,
                               SensorReadError)


class HTTPClient:
    """Basic http client."""

    _connection_pool: urllib3.PoolManager | None = None

    def __init__(self, config: dict):
        """Setup HTTP Client."""
        self.network_name = config.get('name')
        self.prefix = config.get('sensor_prefix')
        self.port = config.get('port', 80)
        self.api_location = config.get('api_location')

        if not self.__class__._connection_pool:
            self.__class__._connection_pool = urllib3.PoolManager()
        self._pool: urllib3.PoolManager = self.__class__._connection_pool

    def read(self, endpoint: str) -> typing.Iterable[sensor_net.SensorData]:
        """Reads sensor data from the endpoint."""
        logger = logging.getLogger("base_http")

        # Sensor are expected to run on RaspberryPie NanoW on an isolated network.
        # The sensors will not provide any HTTPs interface
        url = f"http://{endpoint}:{self.port}{self.api_location}"

        try:
            response: urllib3.HTTPResponse = self._pool.request(
                method='GET',
                url=url,
                timeout=15,
            )
        except urllib3.exceptions.HTTPError as err:
            logger.error("Got HTTP error: %s", err)

            raise SensorNoResponseError(
                url,
                "HTTP connection error: %s" % type(err).__name__,
            )

        if response.status != 200:
            raise SensorReadError(
                endpoint,
                "HTTP Error: %d: %s" % (response.status, response.reason),
            )

        body = response.read()
        logger.debug("Response: %s", body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as err:
            raise SensorDataTypeError(
                endpoint,
                str(err),
            )

        for row in data.get("data", []):
            match row:
                case {"name": name, "value": value, "epoch": epoch}:
                    try:
                        yield sensor_net.SensorData(
                            name,
                            value,
                            datetime.datetime.fromtimestamp(epoch),
                        )
                    except TypeError:
                        raise SensorDataTypeError(
                            endpoint,
                            "Invalid sensor data type.",
                        )
                case _:
                    raise SensorDataTypeError(
                        endpoint,
                        "Invalid sensor data structure.",
                    )


def get_sensor_driver(name: str, config: dict) -> HTTPClient:
    """
    Creates a sensor driver for the given name and configuration.

    :param name: Daemon name
    :param config: configuration for the driver
    :return: HTTPClient instance
    """
    return HTTPClient(config)
