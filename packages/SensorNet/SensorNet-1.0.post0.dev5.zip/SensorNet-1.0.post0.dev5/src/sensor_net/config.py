"""Base configuration manager."""
import dataclasses
import functools
import re
from typing import Generator, Iterable, Iterator

import yaml

from ._ip_iterator import IPRangeIterator, SubnetIterator
from ._plugin_loader import load_backend_driver
from .cron import is_cron_expression
from .drivers import BackendDriver
from .errors import ConfigError


class _EndpointWalker:
    """
    Iterable of endpoint from ip list.

    List of IPs like:
    - 0.0.0.0
    - 0.0.0.0/32
    - 0.0.0.1 - 0.0.0.20
    """

    def __init__(self, ip_list: list[str]):
        """
        Prepare the endpoint walker.

        :param ip_list: List of IP  to walk
        """
        self._list: list[Iterable[str]] = []
        [self._append_group(ip) for ip in ip_list]

    def _append_group(self, ip: str):
        generator = [
            (r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", lambda x: (x, )),  # Encapsulate ip in a tuple
            (r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}$", SubnetIterator),
            ("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3} - "
             "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$", IPRangeIterator),
        ]

        for p, i in generator:
            if re.match(p, ip):
                self._list.append(i(ip))  # type: ignore
                return
        else:
            raise ConfigError("Invalid IP definition: %s" % ip)

    def __iter__(self) -> Iterator[str]:
        """Setup IP list iterator"""
        return self._walker()

    def _walker(self) -> Generator[str, None, None]:
        """Generator that iterates over IP addresses."""
        for ip_group in self._list:
            yield from ip_group


@dataclasses.dataclass
class NetworkConfig:
    """Network configuration class."""

    name: str
    api_endpoints: Iterable[str] = dataclasses.field(init=False, repr=False)
    ip_addresses: list[str]
    sensor_prefix: str
    cron: str
    api_port: int = dataclasses.field(default=80)
    api_location: str = dataclasses.field(default="/")

    def __post_init__(self):
        """
        Completes dataclasses initialization.

        Checks if cron is a valid cron string.
        """
        if not is_cron_expression(self.cron):
            raise ConfigError("Invalid cron expression: %s" % self.cron)

        self.api_endpoints = _EndpointWalker(self.ip_addresses)


@dataclasses.dataclass
class ApplicationConfig:
    """Application configuration class."""

    daemon_name: str
    backend: dict
    driver: BackendDriver = dataclasses.field(init=False)
    networks: list[dict]
    network_setup: list[NetworkConfig] = dataclasses.field(init=False)

    def __post_init__(self):
        """
        Complete dataclass initialization.

        -> Prepare defines network_setup
        -> Loads backend driver module
        -> Retrieve BackendDriver
        """
        self.network_setup = [NetworkConfig(**network) for network in self.networks]

        backend_mod = load_backend_driver(self.backend["driver"])
        self.driver = backend_mod.get_driver(self.daemon_name, self.backend)


@functools.lru_cache(maxsize=1)
def get_configuration(filename: str | None) -> ApplicationConfig:
    """
    Retrieve configuration from file.

    - Read YAML file.
    - Creates and a new ApplicationConfig object

    Caches the configuration object.

    :param filename: [Optional] Configuration YAML file
    :return: Application configuration
    """
    filename = filename or "/etc/sensornet/sensor.yaml"

    try:
        fp = open(filename, 'r')
    except OSError as err:
        raise ConfigError("Failed to open configuration file %s: %s" % (filename, err), err)

    try:
        cfg = yaml.safe_load(fp)
        return ApplicationConfig(**cfg)
    except yaml.YAMLError as err:
        raise ConfigError("Failed to parse configuration file %s: %s" % (filename, err), err)
    except (KeyError, ValueError, TypeError) as err:
        raise ConfigError("Invalid configuration parameter: %s" % err, err)
    finally:
        fp.close()
