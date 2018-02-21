import logging
import os
import sys

from qt_py_convert.color import ANSI, color_text

__BASE_LOGGING_NAME = "QtPyConvert"


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': ANSI.colors.orange,
        'INFO': ANSI.colors.white,
        'DEBUG': ANSI.colors.blue,
        'CRITICAL': ANSI.colors.red,
        'ERROR': ANSI.colors.red
    }

    def __init__(self, fmt, dt=None):
        logging.Formatter.__init__(self, fmt, dt)

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = color_text(
                text=levelname,
                color=self.COLORS[levelname],
                style=ANSI.styles.strong
            )
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def get_formatter(name="%(name)s", name_color=ANSI.colors.purple,
                  name_style=ANSI.styles.plain, msg_color=ANSI.colors.white):

    custom_name = color_text(text=name, color=name_color, style=name_style)
    message = color_text(text="%(message)s", color=msg_color)
    formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s | [" + custom_name + "] " + message,
        "%Y-%m-%d %H:%M:%S"
    )
    return formatter


def get_logger(logger_name, level=None,
               name_color=ANSI.colors.purple, message_color=ANSI.colors.white):

    if not logger_name.startswith(__BASE_LOGGING_NAME):
        logger_name = __BASE_LOGGING_NAME + "." + logger_name

    if level is None:
        level = os.environ.get("LOGLEVEL", logging.INFO)

    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = get_formatter(name_color=name_color, msg_color=message_color)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    handler.setLevel(level)
    logger.setLevel(level)
    return logger
