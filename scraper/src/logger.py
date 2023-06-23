import logging
from functools import wraps


def detailed_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        logger.info("Method '{}' started.".format(func.__name__))
        try:
            result = func(*args, **kwargs)
            logger.info("Method '{}' completed successfully.".format(func.__name__))
            logger.info(f"Number of collected products: {len(result)}")
            return result
        except Exception as e:
            logger.exception("Method '{}' encountered an error: {}".format(func.__name__, str(e)))
            raise
    return wrapper