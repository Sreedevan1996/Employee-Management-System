import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(app):
    """
    Configure application logging.

    - Logs to console by default
    - Logs to file in non-testing environments
    - Ensures logs directory exists
    """
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # Avoid duplicate handlers when app reloads
    if app.logger.handlers:
        for handler in list(app.logger.handlers):
            app.logger.removeHandler(handler)

    app.logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)

    if not app.testing:
        log_dir = Path(app.root_path).parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.propagate = False
    app.logger.info("Logging configured successfully.")