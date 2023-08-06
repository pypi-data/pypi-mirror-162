"""Command line for sensornet.py"""
import argparse
import asyncio
import dataclasses

from ._run import run
from ._version import get_versions
from .defaults import CONFIG_FILE


@dataclasses.dataclass
class SensorNetOptions:
    """Options namespace."""

    daemon: bool = dataclasses.field(default=False)
    debug: bool = dataclasses.field(default=False)
    config: str = dataclasses.field(default=CONFIG_FILE)
    threads: int = dataclasses.field(default=1)


class SensorNetOptionParser(argparse.ArgumentParser):
    """Base option parser for sensornet."""

    def __init__(self, *args, **kwargs):
        """Setup option parser."""
        super().__init__("Read ans store sensor data.")
        self.set_defaults(
            daemon=False,
            debug=False,
            help=False,
            version=False,
            config=CONFIG_FILE,
        )

        # Keep Flags and other options separate and ordered

        # Flags
        self.add_argument(
            "-d",
            "--daemon",
            action="store_true",
            help="Sets sensornet to run as a Daemon.",
        )
        self.add_argument(
            "-D",
            "--debug",
            action="store_true",
            help="Sets sensornet to display debug output.",
        )
        self.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {get_versions()}",
            help="Print version information.",
        )

        # Options
        self.add_argument(
            "-c",
            "--config",
            action="store",
            metavar="FILE",
            help="Configuration file to use.",
        )
        self.add_argument(
            "-t",
            "--threads",
            action="store",
            type=int,
            help="Number of concurrent workers threads to use.",
        )


def main(argv: list[str] | None = None) -> int:
    """
    Main function.

    :param argv: Command line arguments, if None sys.argv is used.
    :return: Command line exit status
    """
    parser = SensorNetOptionParser()
    options = SensorNetOptions()
    parser.parse_args(args=argv, namespace=options)

    return asyncio.run(run(
        config=options.config,
        daemon=options.daemon,
        threads=options.threads,
    ))


if __name__ == '__main__':
    main()
