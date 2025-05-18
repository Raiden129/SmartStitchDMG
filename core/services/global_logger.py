import functools
import logging
import os
import sys
from datetime import datetime

from ..utils.constants import LOG_REL_DIR

class GlobalLogger:
    @classmethod
    def configureGlobalLogger(self):
        """Initializes and Configures Logging Service"""
        # Determine log directory based on environment
        if getattr(sys, 'frozen', False):  # Running as a PyInstaller bundle
            # Use ~/Library/Logs/SmartStitch for bundled app
            log_dir = os.path.expanduser('~/Library/Logs/SmartStitch')
        else:
            # Use LOG_REL_DIR for development
            log_dir = LOG_REL_DIR

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        current_date = datetime.now()
        log_filename = current_date.strftime('log-%Y-%m-%d.log')
        log_filename = os.path.join(log_dir, log_filename)

        log_level = logging.DEBUG
        log_format = '%(levelname)s:%(asctime)s:%(message)s'
        logging.basicConfig(format=log_format, filename=log_filename, level=log_level)
        logging.debug('GlobalLogger:Logger Initialized')
        # Remove PIL logging from polluting the Debug Level
        pil_logger = logging.getLogger('PIL')
        pil_logger.setLevel(logging.INFO)

    @classmethod
    def log_warning(self, message, caller='GlobalLogger', *args, **kwargs):
        log_msg = f'{caller}:{message}'
        logging.warning(log_msg, *args, **kwargs)

    @classmethod
    def log_debug(self, message, caller='GlobalLogger', *args, **kwargs):
        log = f'{caller}:{message}'
        logging.debug(log, *args, **kwargs)

def logFunc(func=None, inclass=False):
    if func is None:
        return functools.partial(logFunc, inclass=inclass)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        caller_class = "GlobalLogger"
        args_repr = [repr(a) for a in args]
        if inclass:
            caller_class = type(args[0]).__name__
            args_repr = [repr(args[i]) for i in range(1, len(args))]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        GlobalLogger.log_debug(f'{func.__name__}:args:{signature}', caller_class)
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logging.exception(
                f"Exception raised in {func.__name__}. exception: {str(e)}"
            )
            raise e

    return wrapper

GlobalLogger.configureGlobalLogger()
