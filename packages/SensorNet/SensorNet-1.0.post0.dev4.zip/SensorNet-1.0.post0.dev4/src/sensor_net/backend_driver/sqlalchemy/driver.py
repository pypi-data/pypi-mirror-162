"""SQLAlchemy backend driver."""
import datetime
from typing import Iterable

import sqlalchemy.exc
from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Engine

from sensor_net import SensorData
from sensor_net.errors import BackendWriteError

from ._logger import logger


class SQLAlchemyDriver:
    """SQLAlchemy backend driver."""

    def __init__(self, name: str, engine: Engine, meta: MetaData, table: Table):
        """
        Creates a new Backend Driver for SQLAlchemy.

        The drivers perform a simple INSERT into public.d_sensor_metrics.

        :param name: Name of the daemon.
        :param engine: SQLAlchemy engine to use.
        :param meta: Meta object related to the backend.
        :param table: SQLAlchemy table to use.
        """
        self._engine = engine
        self._table = table
        self._name = name
        self._meta = meta

    @property
    def engine(self) -> Engine:
        """The SQLAlchemy Engine."""
        return self._engine

    @property
    def name(self) -> str:
        """Daemon name."""
        return self._name

    @property
    def table(self) -> Table:
        """Metric table object."""
        return self._table

    def write(self, network_name: str, network_prefix: str, sensor_address: str,
              data: Iterable[SensorData]) -> int:
        """
        Inserts or updates data into the destination table.

        :param network_name: The name of the network
        :param network_prefix: prefix of the network
        :param sensor_address: sensor address
        :param data: Collection of sensor data to insert into d_sensor_metrics.
        :return: Number of rows inserted
        """
        def _cast() -> list[dict]:
            return [{
                "daemon": self._name,
                "sensor": f"{network_prefix}{sensor_address}",
                "network": network_name,
                "metric_name": d.name,
                "metric_date_utc": d.datetime_utc,
                "metric_value": d.value,
                "d_created_utc": datetime.datetime.utcnow(),
            } for d in data]

        try:
            with self._engine.connect() as conn:
                logger.info("Inserting new rows.")
                rows = _cast()
                result = conn.execute(self._table.insert().values(rows))
                logger.info(repr(result))
                return len(rows)

                # conn.commit()
        except sqlalchemy.exc.SQLAlchemyError as err:
            message = "Error writing to d_sensor_metrics: %s %s" % (
                err.code,
                str(err),
            )
            logger.error(message)
            raise BackendWriteError(
                backend_name=self.name,
                message=message,
            )
