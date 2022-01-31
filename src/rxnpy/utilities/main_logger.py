"""
Look up Logger


"""

import logging


colors = {
    "reset": "\033[0m",  # add at the end to stop coloring
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "gray": "\033[37m",
}

b_colors = {  # bold colors
    "reset": "\u001b[0m",  # add at the end to stop coloring
    "black": "\u001b[30;1m",
    "red": "\u001b[31;1m",
    "green": '\u001b[32;1m',
    "yellow": "\u001b[33;1m",
    "blue": "\u001b[34;1m",
    "magenta": "\u001b[35;1m",
    "cyan": "\u001b[36;1m",
    "white": "\u001b[37;1m",
}

BOLD_SEQ = "\033[1m"


class LogFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s", datefmt=None, style='%')

    def format(self, record):
        # Save the original format configured by the user when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = f"\t \t{colors['gray']}%(msg)s{colors['reset']}"
        elif record.levelno == logging.INFO:
            self._style._fmt = f"\t{b_colors['magenta']}%(msg)s{b_colors['reset']}"
        elif record.levelno == logging.WARNING:
            self._style._fmt = f"{colors['yellow']}WARNING: %(msg)s {colors['reset']}"
        elif record.levelno == logging.ERROR:
            self._style._fmt = f"{colors['red']}ERROR: %(msg)s {colors['reset']}"
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = f"{colors['red']}ERROR: %(msg)s {colors['reset']}"

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


logger_rxnpy = logging.getLogger("logger_rxnpy")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(LogFormatter())
logger_rxnpy.addHandler(stream_handler)

logger_rxnpy.setLevel(logging.WARNING)
