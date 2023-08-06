"""Handles dynamic plugin loading"""
import importlib
import types
import typing

from ._logger import get_logger
from .drivers import BackendDriver
from .errors import ConfigError, MissingDriverError


def load_plugin(module_name: str, sub_dir: str) -> types.ModuleType:
    """
    Loads module_name from ./sub_dir

    :param module_name: Name of the module to load.
    :param sub_dir: Sub directory of the module, relative to this file.
    :return: Module object
    """
    sub_dir = sub_dir.replace("/", ".")
    module = f"sensor_net.{sub_dir}.{module_name}"

    get_logger().debug("Loading module %s", module)
    return importlib.import_module(module)


class BackendModule(typing.Protocol):
    """Required features for a backend module."""

    def get_driver(self, name: str, cfg: dict) -> BackendDriver:
        """Retrieves the sensor driver."""
        ...


def is_backend_driver_module(module: types.ModuleType) -> typing.TypeGuard[BackendModule]:
    """Ensures that module is a backend driver module."""
    if not hasattr(module, 'get_driver'):
        return False

    if not callable(module.get_driver):
        return False

    # We can't predict parameters names, nor return value type.
    get_logger().debug("Got get_driver annotations %s", repr(module.get_driver.__annotations__))
    if len(module.get_driver.__annotations__) == 2:
        name, conf = module.get_driver.__annotations__.values()
    elif len(module.get_driver.__annotations__) == 3:
        name, conf, _ = module.get_driver.__annotations__.values()
    else:
        return False

    return name is str and conf is dict


def load_backend_driver(module_name: str) -> BackendModule:
    """
    Loads module_name and ensure it is a backend driver module.

    :param module_name: Name of the module
    :return: BackendModule
    """
    get_logger().info("Loading backend driver: %s", module_name)
    try:
        module = load_plugin(module_name, "backend_driver")
    except ModuleNotFoundError:
        raise MissingDriverError(module_name)

    if not is_backend_driver_module(module):
        raise ConfigError("Module '%s' does not contain a backend driver." % module_name)

    return module  # type: ignore
