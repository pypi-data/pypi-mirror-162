"""Actually runs the script."""
import asyncio
import typing

from sensor_net.errors import BackendError, ConfigError, SensorError

from ._logger import get_logger
from .config import ApplicationConfig, NetworkConfig, get_configuration
from .drivers import SensorDriver
from .sensor_driver.base_http import get_sensor_driver

OK, ERR = 0, 1


async def run(config: str, daemon: bool, threads: int):
    """
    Loads the configuration and runs the scripts.

    :param config: Configuration file to use.
    :param daemon: if true, the script will sleep queue new sensor polling every minute.
    :param threads: number of threads to use.
    :return: OK | ERR
    """
    logger = get_logger()
    work_queue: asyncio.Queue[tuple[NetworkConfig, SensorDriver, str]] = asyncio.Queue()

    daemon_event = asyncio.Event()

    logger.debug("Starting %s workers", threads)

    r = OK
    if not daemon:
        daemon_event.set()

    try:
        cfg = await add_polls(config, work_queue)
        if not cfg:
            return ERR

        await asyncio.gather(*[
            poll(i, work_queue, daemon_event, cfg)
            for i in range(min(threads, work_queue.qsize()) or 1)
        ])
    except SystemExit:
        daemon_event.set()
    except ConfigError as err:
        logger.error(err)
        daemon_event.set()
        r = ERR

    return r


async def add_polls(
        config: str,
        work_queue: asyncio.Queue[tuple[NetworkConfig, SensorDriver, str]],
) -> ApplicationConfig | None:
    """
    Loads the configuration and adds api endpoints to the queue.

    :param config: Configuration file to use.
    :param work_queue: Configuration queue to add.
    :return: The application configuration object or None
    """
    logger = get_logger()

    logger.info("Loading configuration from %s", config)
    try:
        cfg = get_configuration(config)
    except ConfigError as err:
        logger.error("Error loading configuration: %s", err)
        return None

    [await work_queue.put(e) for e in iter_endpoints(cfg)]  # type: ignore

    return cfg


def iter_endpoints(
        config: ApplicationConfig,
) -> typing.Generator[tuple[NetworkConfig, SensorDriver, str], None, None]:
    """
    Returns a callable to each network endpoint defined in the configuration.

    :param config: Application configuration.
    """
    for network in config.network_setup:
        driver = get_sensor_driver(network.name, network.__dict__)

        for n in network.api_endpoints:
            yield network, driver, n


async def poll(
        num: int,
        queue: asyncio.Queue[tuple[NetworkConfig, SensorDriver, str]],
        daemon: asyncio.Event,
        cfg: ApplicationConfig,
):
    """
    Run calls to the sensor endpoints.

    :param num: Worker number
    :param queue: Queue to watch.
    :param daemon: Daemon end event
    :param cfg: Configuration of the application.
    """
    logger = get_logger()

    while True:
        try:
            network, driver, endpoint = queue.get_nowait()
        except asyncio.QueueEmpty:
            logger.debug("Queue is empty.")
            return

        logger.debug("Worker %(num)d polling %(endpoint)s...", num, endpoint)

        try:
            data = driver.read(endpoint)

            count = cfg.driver.write(
                network.name,
                network.sensor_prefix,
                endpoint,
                data,
            )
            logger.info(
                "poll\t%s\t%s\tmetrics=%d",
                cfg.daemon_name,
                endpoint,
                count,
            )
        except SensorError as err:
            logger.error(
                "Error reading sensor %s: %s",
                endpoint,
                err.message,
            )
        except BackendError as err:
            logger.error(
                "Error while writing data from %s: %s",
                endpoint,
                err.message,
            )

        queue.task_done()
        if daemon.is_set():
            break
