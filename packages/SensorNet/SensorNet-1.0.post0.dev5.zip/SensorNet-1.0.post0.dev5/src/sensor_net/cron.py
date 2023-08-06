"""Handles the cron logic."""
import datetime
import functools
import typing

from croniter import croniter


@functools.lru_cache(maxsize=10)
def is_triggered(cron_expression: str, utc_now: datetime.datetime) -> bool:
    """
    Checks if a cron expression is triggered.

    A cron expression is triggered if the next run is matching the current time to the minute.

    :param cron_expression: String representing the cron expression "m h M Y W"
    :param utc_now: Current timestamp in UTC
    :return: True if the cron expression is triggered, False otherwise.
    """
    cron = croniter(
        expr_format=cron_expression,
        start_time=utc_now - datetime.timedelta(minutes=1),
        ret_type=datetime.datetime,
    )
    return cron.get_next() <= utc_now


def is_cron_expression(expression: str) -> typing.TypeGuard[str]:
    """
    Checks if a string represents a cron expression.

    :param expression: Expression to check
    :return: True is str is a valid cron expression, False otherwise.
    """
    return croniter.is_valid(expression)
