import logging


def setup_logging(to_console=True, to_file=False):
    level = logging.INFO
    format = "%(asctime)-15s %(levelname)-9s: %(name)-8s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    file = "./logs/application.log"

    handlers = []
    if to_console:
        handlers.append(logging.StreamHandler())
    if to_file:
        handlers.append(
            logging.RotatingFileHandler(file, maxBytes=10485760, backupCount=10)
        )

    logging.basicConfig(handlers=handlers, level=level, format=format, datefmt=datefmt)
