import logging
from logging.handlers import TimedRotatingFileHandler


class ConfigLogging:
    def __init__(self):
        self.path = "logs/"

    def setup_logger(self):
        pattern = "%(asctime)s | %(levelname)s | %(filename)s -> %(funcName)s():%(lineno)s | %(message)s"
        logger = logging.getLogger("parser")
        logger.setLevel(logging.DEBUG)

        info_handler = TimedRotatingFileHandler(
            filename=self.path + "parser-info.log",
            when="midnight",
            interval=1,
            backupCount=10,
            encoding="utf-8"
        )
        info_handler.setLevel(logging.INFO)
        info_handler.addFilter(lambda record: record.levelno == logging.INFO)
        info_handler.suffix = "%Y-%m-%d"
        formatter = logging.Formatter(pattern)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        error_handler = TimedRotatingFileHandler(
            filename=self.path + "parser-error.log",
            when='midnight',
            interval=1,
            backupCount=10,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.suffix = "%Y-%m-%d"
        logger.addHandler(error_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        return logger
