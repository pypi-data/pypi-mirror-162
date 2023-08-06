"""All IP Range iterables."""
import ipaddress
import re
import typing

import sensor_net.errors


class SubnetIterator:
    """
    Iters all IP Addresses in a subnet

    :attribute network: IP network
    """

    def __init__(self, network: str):
        """Instantiates the iterator"""
        try:
            self.network = ipaddress.ip_network(network)
        except ValueError as err:
            raise sensor_net.errors.ConfigError(
                "Invalid network address: %s" % network,
                err,
            )

    def __iter__(self) -> typing.Iterable[str]:
        """Setup IP Iterator."""
        return self._ip_generator()

    def _ip_generator(self) -> typing.Generator[str, None, None]:
        """Yields IP addresses."""
        for ip in self.network.hosts():
            yield str(ip)


class IPRangeIterator:
    """Iters in an IP Range."""

    def __init__(self, range: str):
        """Instantiates the iterator."""
        try:
            mn, mx = re.split(r"\s-\s", range)
            self.min = ipaddress.IPv4Address(mn)
            self.max = ipaddress.IPv4Address(mx)
        except ValueError:
            raise sensor_net.errors.ConfigError("Invalid IP Range: %s" % range)

    def __iter__(self) -> typing.Iterator[str]:
        """Starts iteration."""
        return self._ip_generator()

    def _ip_generator(self) -> typing.Generator[str, None, None]:
        """Yields IP addresses."""
        for ip in range(int(self.min), int(self.max) + 1):
            yield str(ipaddress.IPv4Address(ip))
