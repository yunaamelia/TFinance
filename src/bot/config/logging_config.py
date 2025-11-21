"""Logging configuration for FinancialAssist bot."""

import logging
import sys
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for better readability in development."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get color for log level
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET if color else ""

        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Format module name (shorten long paths)
        module = record.name
        if "." in module:
            parts = module.split(".")
            if len(parts) > 2:
                module = ".".join(parts[-2:])  # Keep last 2 parts

        # Build log message
        level_name = f"{color}{self.BOLD}{record.levelname:8}{reset}"
        module_name = f"\033[90m{module:25}\033[0m"  # Gray, fixed width

        message = f"{timestamp} | {level_name} | {module_name} | {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter without colors (for non-TTY outputs)."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format."""
        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Format module name (shorten long paths)
        module = record.name
        if "." in module:
            parts = module.split(".")
            if len(parts) > 2:
                module = ".".join(parts[-2:])  # Keep last 2 parts

        # Build log message
        level_name = f"{record.levelname:8}"
        module_name = f"{module:25}"  # Fixed width

        message = f"{timestamp} | {level_name} | {module_name} | {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


def setup_logging(
    log_level: str = "INFO",
    environment: str = "development",
    log_file: Path | None = None,
) -> None:
    """Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment (development/production)
        log_file: Optional log file path for production
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # Check if stdout is a TTY (terminal)
    use_colors = sys.stdout.isatty() and environment.lower() == "development"

    # Console handler with colored/human-readable format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_colors:
        console_formatter = ColoredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        console_formatter = HumanReadableFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for production (JSON format for log aggregation)
    if log_file and environment.lower() == "production":
        try:
            from logging import handlers

            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = handlers.RotatingFileHandler(
                str(log_file),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
            file_handler.setLevel(level)

            # Use JSON format for production logs (for log aggregation tools)
            json_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"name": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(json_formatter)
            root_logger.addHandler(file_handler)

            logger = logging.getLogger(__name__)
            logger.info("Production file logging enabled", extra={"log_file": str(log_file)})
        except (PermissionError, OSError) as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not setup file logging: {e}")

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Keep our application logs at the configured level
    logging.getLogger("src.bot").setLevel(level)
