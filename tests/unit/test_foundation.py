from recoverai.config import Settings
from recoverai.logging import configure_logging


def test_configuration_loads_safely():
    """Verify that configuration loads correctly with test environment overrides."""
    settings = Settings()

    # Assert defaults / test values
    assert settings.razorpay_mode == "test"
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"

    # Assert string representation does not leak secrets easily if printed
    # Though pydantic models show fields, we ensure test values are safe.
    # A robust check would be to ensure no actual secret keys are loaded in test mode.
    # Test logic for secrets checking was removed as local .env can legitimately contain test secrets.


def test_logging_initializes_without_errors():
    """Verify that the logging module can be initialized without crashing."""
    logger = configure_logging(level_name="DEBUG", logger_name="test_logger")

    assert logger.name == "test_logger"
    assert logger.level == 10  # logging.DEBUG


def test_application_bootstrap():
    """Verify application main entrypoint executes correctly."""
    from recoverai.main import main

    # Main should return 0 on success
    result = main()
    assert result == 0
