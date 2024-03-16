import os
import logging
import click


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }

    def format(self, record):
        log_message = super(ColoredFormatter, self).format(record)
        log_level = record.levelname
        color = self.COLORS.get(log_level, 'white')

        # Include information about the calling module, function, and line number
        caller_info = f'[{record.levelname}] - [{record.module}] - [{record.funcName}:{record.lineno}]'
        log_message = f'{caller_info} - {log_message}'

        return click.style(log_message, fg=color)


class Logger:

    def __init__(self, log_file=None, log_dir="logs", logger_name=None, level=logging.DEBUG):
        if not log_file:
            log_file = f"{os.environ.get('HOSTNAME', 'server')}.log"

        log_dir_path = os.path.join(os.getcwd(), log_dir, os.environ.get('HOSTNAME', ''))
        os.makedirs(log_dir_path, exist_ok=True)
        self.log_file = os.path.join(log_dir_path, log_file)

        self.logger = logging.getLogger(logger_name or __name__)
        self.logger.setLevel(level)

        formatter = ColoredFormatter(
            '[%(asctime)s] -- %(message)s',
            datefmt='%H:%M:%S',
        )

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
