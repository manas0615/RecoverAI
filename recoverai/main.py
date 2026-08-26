import sys

from recoverai.config import settings
from recoverai.logging import configure_logging


def main() -> int:
    """
    Minimal application bootstrap.
    Proves that configuration loads, logging initializes, and the process can run.
    """
    logger = configure_logging(level_name=settings.log_level)

    try:
        logger.info(
            f"Starting RecoverAI foundation in {settings.environment} environment..."
        )
        logger.info(f"Razorpay Mode: {settings.razorpay_mode}")
        logger.info("Application bootstrap completed successfully.")

        # In a real app, this is where the main event loop, web server, or worker would start.
        # For Package 01, we just return success.

        return 0
    except Exception:  # noqa: BLE001
        logger.error("A fatal error occurred during startup.")
        # Do not log the exception details directly if they might contain secrets.
        # In this minimal foundation, we just exit with a failure code.
        return 1


if __name__ == "__main__":
    sys.exit(main())
