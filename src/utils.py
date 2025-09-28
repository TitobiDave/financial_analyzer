import logging


def setup_logging(level: str = "INFO") -> None:
    """
    Configures the root logger with a standard format and logging level.

    Args:
        level (str, optional): Logging level as a string (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
                               Defaults to "INFO".

    Returns:
        None
    """
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger().setLevel(level)
