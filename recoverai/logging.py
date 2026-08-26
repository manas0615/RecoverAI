import logging
import sys


def configure_logging(
    level_name: str = "INFO", logger_name: str | None = None
) -> logging.Logger:
    """
    Configures minimal structured logging foundation for RecoverAI.
    Outputs logs to stdout with a standard format.
    Does not overbuild OpenTelemetry.
    """
    level = getattr(logging, level_name.upper(), logging.INFO)

    # Create the root logger or a specific named logger
    logger = logging.getLogger(logger_name if logger_name else "recoverai")
    logger.setLevel(level)

    # Avoid adding multiple handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Simple structured format: [timestamp] [level] [logger] message
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent log messages from being duplicated in the root logger if a specific name is provided
        logger.propagate = False

    return logger


# Create a default logger instance for easy import
log = configure_logging()
