"""SQLAlchemy driver configuration"""
import dataclasses
import os

import sqlalchemy

from .driver import SQLAlchemyDriver
from .schema import Schema


@dataclasses.dataclass
class SQLAlchemyConfig:
    """
    Defines SQLAlchemy base configuration settings.

    :attribute driver: Always "SQLAlchemy"
    :attribute url: SQLAlchemy URL
    """

    url: str
    driver: str = dataclasses.field(default="sqlalchemy")


def _get_config(config: dict) -> SQLAlchemyConfig:
    """
    Retrieve SQLAlchemy configuration settings.

    :param config: Dict created from sensor.yaml
    :return: SQLAlchemy configuration settings.
    """
    env_url = os.getenv("SQL_DRIVER_URL")
    return SQLAlchemyConfig(
        url=config.get("url", env_url),
    )


def get_driver(name: str, config: dict) -> SQLAlchemyDriver:
    """
    Instantiates a SQLAlchemy driver.

    :param name: Name of the daemon
    :param config: Dict created from sensor.yaml backend section.
    :return: SQLAlchemy driver instance.
    :raises ConfigurationError: if the configuration is invalid.
    :raises BackendError: if failed to instantiate correctly.
    """
    cnf_object = _get_config(config)
    engine = sqlalchemy.create_engine(cnf_object.url)

    schema = Schema()

    return SQLAlchemyDriver(
        name,
        engine,
        schema.metadata,
        schema.metrics_table,
    )
