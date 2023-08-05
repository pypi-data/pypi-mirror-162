import logging


def log_exception(source: str, exception: Exception):
    """
    To log exception to console
    usage: log_exception(MyClass, exception_object)
    
    :param source: 
    :param exception: 
    :return: 
    """
    logger = logging.getLogger(source)
    logger.exception(exception)
