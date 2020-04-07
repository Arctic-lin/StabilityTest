import logging
import os

from configs import GetConfigs


def createlogger(name):
    """Create a logger named specified name with the level set in config file.
    return a logger
    """
    config = GetConfigs("common")
    lev_key = config.getstr("LOG_FITER", "Default", "common").upper()
    lev_dict = {"DEBUG": logging.DEBUG, "INFO": logging.INFO,
                "WARNING": logging.WARNING, "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL}
    logger = logging.getLogger(name)
    logger.setLevel(lev_dict[lev_key])
    if not len(logger.handlers):
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d: [%(levelname)s] [%(name)s] [%(funcName)s][%(lineno)d] %(message)s',
            '%y%m%d %H:%M:%S')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def create_folder():
    """Create folder to save pic & log.
    Return a folder path or None
    Exception: OSError
    """
    log_path = os.environ.get("LOG_PATH")
    if log_path is None:
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    if not os.path.exists(log_path):
        get_common_logger().debug("log_path not exsit")
        os.makedirs(log_path)
    fail_img_dir = os.path.join(log_path, 'fail_img')
    if not os.path.exists(fail_img_dir):
        get_common_logger().debug("fail_img not exsit")
        os.makedirs(fail_img_dir)
    if not os.path.exists(log_path):
        return None
    return log_path


def get_common_logger():
    return logging.getLogger('COMMON')
