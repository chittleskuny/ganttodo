import logging


def init_logger():
    logger = logging.getLogger()
    format = '%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s'
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(format))
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
