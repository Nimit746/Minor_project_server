# import os
# import logging
# from pathlib import Path
# from logging.handlers import RotatingFileHandler
# from app.config.settings import get_settings

# BASE_DIR = Path(__file__).resolve().parents[2]
# LOG_DIR = BASE_DIR / 'logs'
# LOG_DIR.mkdir(parents=True, exist_ok=True)
# LOG_FILE = LOG_DIR / 'app.log'
# settings = get_settings()


# class CleanConsoleFormatter(logging.Formatter):
#     """
#     Prevents raw exceptions tracebacks from apearing in normal console logging.
#     """


#     def format(self, record):
#         record = logging.makeLogRecord(record.__dict__)

#         record.exc_info = None
#         record.exc_test = None

#         return super().format(record)



# def setup_logging():
#     settings = get_settings()
#     level_name = settings.log_level.upper()
#     level = getattr(logging, level_name, logging.INFO)

#     console_format = (
#         '%(asctime)s | %(levelname)-8s'
#         '%(name)s | %(message)s'
#     )

#     file_format = (
#         "%(asctime)s | %(levelname)-8s | "
#         "%(name)s:%(lineno)d | %(message)s"
#     )


#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(level)
#     console_handler.setFormatter(
#         CleanConsoleFormatter(console_format)
#     )


#     file_handler = RotatingFileHandler(
#         LOG_FILE,
#         maxBytes = 5 * 1024 * 1024,
#         backupCount = 5,
#         encoding = 'utf-8'
#     )


#     file_handler.setLevel(logging.DEBUG)
#     file_handler.setFormatter(
#         logging.Formatter(file_format)
#     )


#     root_logger = logging.getLogger()
#     root_logger.setLevel(logging.DEBUG)


#     if not getattr(root_logger, '_configured', False):
#         root_logger.handlers.clear()
#         root_logger.addHandler(console_handler)
#         root_logger.addHandler(file_handler)
#         root_logger._configured = True



# def get_logger(name: str) -> logging.Logger:
#     return logging.getLogger(name)



# def log_exception(
#     logger: logging.Logger,
#     message: str,
#     exc: Exception
# ):
#     logger.error(
#         '%s  | Exception: %s',
#         message,
#         type(exc).__name__,
#         exc_info=(type(exc), exc, exc.__traceback__),
# )





import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    if not any(getattr(h, "_app_handler", False) for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler._app_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        root.addHandler(handler)
