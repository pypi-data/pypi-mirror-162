"""SQLAlchemy data schema"""
import sqlalchemy


class Schema:
    """Represent SQLAlchemy tables"""

    def __init__(self):
        """Create all tables in the Meta."""
        self._meta = sqlalchemy.MetaData()
        self._metrics_table = sqlalchemy.Table(
            "d_sensor_metrics",
            self._meta,
            sqlalchemy.Column("daemon", sqlalchemy.String(length=100), nullable=False),
            sqlalchemy.Column("sensor", sqlalchemy.String(length=300), nullable=False),
            sqlalchemy.Column("network", sqlalchemy.String(length=100), nullable=True),
            sqlalchemy.Column("metric_name", sqlalchemy.String(length=300), nullable=False),
            sqlalchemy.Column("metric_date_utc", sqlalchemy.TIMESTAMP(), nullable=False),
            sqlalchemy.Column("metric_value", sqlalchemy.Numeric(36, 15), nullable=True),
            sqlalchemy.Column("d_created_utc", sqlalchemy.TIMESTAMP(), nullable=False),
        )

    def setup(self, engine: sqlalchemy.engine.Engine):
        """Creates all tables in the Meta."""
        self._meta.create_all(engine)

    @property
    def metadata(self) -> sqlalchemy.MetaData:
        """Schema metadata"""
        return self._meta

    @property
    def metrics_table(self) -> sqlalchemy.Table:
        """Schema metrics table"""
        return self._metrics_table
