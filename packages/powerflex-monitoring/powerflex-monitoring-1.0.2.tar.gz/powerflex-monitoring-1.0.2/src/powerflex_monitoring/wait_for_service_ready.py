#!/usr/bin/env python3
import logging
import sys
from argparse import ArgumentParser
from typing import Callable, List, NoReturn, Optional, Union

import backoff
import requests

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
no_color_formatter = logging.Formatter("[%(levelname)s] %(message)s")

color_formatter: Union[logging.Formatter, "colorlog.ColoredFormatter"]
try:
    import colorlog  # This is an optional dependency

    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s %(message)s"
    )
except ImportError:  # pragma: no cover
    # Mocking an ImportError in unit tests looks tricky
    color_formatter = no_color_formatter

handler.setFormatter(color_formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def make_wait_for_service_ready(
    max_retry_seconds: float, retry_delay_sec: float
) -> Callable[[str], NoReturn]:
    exceptions = (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.JSONDecodeError,
        RuntimeError,
    )

    @backoff.on_exception(
        backoff.constant,
        exceptions,
        logger=logger,
        jitter=None,
        max_time=max_retry_seconds,
        interval=retry_delay_sec,
    )
    def wait_for_service_ready(url: str) -> NoReturn:
        response = requests.get(url)
        response.raise_for_status()
        logger.debug("%s (status %s): %s", url, response.status_code, response.text)

        ready_status = response.json()

        if ready_status["ready"] is not True:
            raise RuntimeError(f"Service is not ready: {ready_status}")

        logger.info("Service is ready :)")
        sys.exit(0)

    def wait_for_service_ready_wrapped(url: str) -> NoReturn:
        try:
            wait_for_service_ready(url)
        except exceptions:
            logger.critical("Service did not become ready", exc_info=True)
            sys.exit(2)

    return wait_for_service_ready_wrapped


def main(argv: Optional[List[str]] = None) -> NoReturn:
    if argv is None:  # pragma: no cover
        argv = sys.argv[1:]
    argparser = ArgumentParser(
        description="Wait for a given service to mark itself ready"
    )
    argparser.add_argument("--ready-check-url", "--url", "-u", required=True)
    argparser.add_argument("--max-retry-seconds", type=int, default=7)
    argparser.add_argument("--retry-delay_sec", type=float, default=1 / 3)
    argparser.add_argument("--quiet", action="store_true")
    argparser.add_argument("--no-color", action="store_true")

    args = argparser.parse_args(argv)

    if args.quiet:
        logger.setLevel(logging.INFO)

    if args.no_color:
        handler.setFormatter(no_color_formatter)

    wait_for_service_ready = make_wait_for_service_ready(
        args.max_retry_seconds, args.retry_delay_sec
    )

    wait_for_service_ready(args.ready_check_url)


if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Goodbye")
        sys.exit(0)
