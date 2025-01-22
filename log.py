import logging

class CustomFormatter(logging.Formatter):

    grey_ = "\x1b[37;21m"
    grey = "\x1b[37;2m"
    yellow = "\x1b[33;2m"
    red = "\x1b[31;2m"
    bold_red = "\x1b[31;21m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey_ + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# create logger with 'spam_application'
logger = logging.getLogger("My_app")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)
logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format="%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
                    datefmt='%H:%M:%S.%3d',
                    level=logging.DEBUG)
###
