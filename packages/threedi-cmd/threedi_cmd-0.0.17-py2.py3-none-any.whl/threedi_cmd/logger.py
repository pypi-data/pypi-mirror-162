import logging
from rich.logging import RichHandler
from functools import lru_cache


@lru_cache()
def get_logger(level: str):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger("rich")
    return logger
