"""Backend driver Stub package"""
import typing
import unittest.mock

import sensor_net
from sensor_net.errors import BackendConfigError, BackendWriteError


class StubBackendDriver:
    """Stub backend driver."""

    def __init__(self, name: str, parent: 'StubBackend'):
        """
        Initialize the StubBackendDriver

        :param parent: StubBackend attached to this backend driver.
        """
        self.__parent = parent
        self.__name = name
        self.__parent.register_driver(name, self)

    def write(
            self,
            network_name: str,
            network_prefix: str,
            sensor_address: str,
            data: typing.Iterable[sensor_net.SensorData],
    ):
        """
        Register writes to the stub backend

        :param network_name: Network name, not used
        :param network_prefix: Network prefix, not used
        :param sensor_address: Sensor address, not used
        :param data: Sensor data, stored in the stub backend writes
        """
        dts = [d for d in data]
        self.__parent.register_write(
            self.__name,
            dts,
        )

        return len(dts)


class StubBackend:
    """
    Complete backend stub.

    >>> import datetime
    >>> stub = StubBackend()
    >>> stub.start()
    >>> backend_driver = get_driver("stub", {})
    >>> data = sensor_net.SensorData("heartbeat", 0, datetime.datetime.utcnow())
    >>> backend_driver.write("stub_net", "stb", "0.0.0.0", [data])
    >>> assert len(stub.writes) == 1
    >>> stub.stop()

    :attribute writes: List of tuples (driver name, write call attributes)
    :attribute drivers: List of drivers name registered
    :attribute config_error: get_driver will raise a BackendConfigError if True
    :attribute write_error: write will raise a BackendWriteError if True
    """

    instance: typing.Optional["StubBackend"] = None

    def __init__(self, config_error: bool = False, write_error: bool = False):
        """
        Creates a new StubBackend

        :param config_error: get_driver will raise a BackendConfigError if True
        :param write_error: write will raise a BackendWriteError if True
        """
        self.config_error = config_error
        self.write_error = write_error
        self._drivers: dict[str, StubBackendDriver] = {}
        self._writes: list[tuple[str, sensor_net.SensorData]] = []
        self._patch = unittest.mock.patch(
            "sensor_net.backend_driver.stubber.get_driver",
            new=self.__call__,
        )

    def start(self):
        """Begin the stub of backend driver."""
        self._patch.start()

    def __enter__(self):
        """Starts mocking."""
        self.start()

    def stop(self):
        """Stops mocking."""
        self._patch.stop()

    def __exit__(self, exc_type, exc_val, exc):
        """Stops mocking."""
        self.stop()

    def __call__(self, name: str, configuration: dict) -> StubBackendDriver:
        """Replaces get_config while stubbing"""
        if self.config_error:
            raise BackendConfigError(name, "Stub sets to raise an exception.")
        return StubBackendDriver(name, self)

    def register_driver(self, name: str, driver: StubBackendDriver):
        """
        Registers a new driver

        :param name: Driver name
        :param driver: Driver instance
        """
        self._drivers[name] = driver

    def register_write(self, name: str, write: list[sensor_net.SensorData]):
        """
        Registers write to the backend driver.

        :param name: Driver name
        :param write: list of sensor data
        """
        if self.write_error:
            raise BackendWriteError(name, "Stub sets to raise an exception.")

        self._writes.extend(((name, d) for d in write))

    @property
    def drivers(self) -> dict[str, StubBackendDriver]:
        """Maps to driver_name -> driver"""
        return self._drivers

    @property
    def writes(self) -> list[tuple[str, sensor_net.SensorData]]:
        """List of all writes send to this stub"""
        return self._writes


def get_driver(name: str, config: dict):
    """Returns a StubDriver."""
    if not StubBackend.instance:
        raise RuntimeError("StubBackend is not available.")
    return StubBackend.instance(name, config)
