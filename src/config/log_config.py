import os
import sys
from datetime import datetime
import logging.handlers


def setup_logger(save=False) -> logging.handlers:
    """

    :return:
    """
    logger = logging.getLogger('__main__')
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    # formatter = logging.Formatter(f"%(asctime)s [%(levelname)s] %(message)-60s @(%(filename)s:%(lineno)d)")
    formatter = logging.Formatter(f"%(asctime)s [%(levelname)s] %(message)s")

    # Create a stream handler and add formatter
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Create the save folder and file handler
    if save:
        path = './log'
        dt = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

        # Check the save folder
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        file_handler = logging.FileHandler(f"{path}/{dt}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
