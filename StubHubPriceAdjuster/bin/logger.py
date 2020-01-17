

import logging 
from logging.handlers import RotatingFileHandler

class LoggerNot():

    logger = None

    def __init__(self, path):
        """
        Creates a rotating log
        """
        self.logger = logging.getLogger("Rotating Log")
        self.logger.setLevel(logging.DEBUG)
     
        # add a rotating handler
        handler = RotatingFileHandler(path, maxBytes=(1024*1000), backupCount=5)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s]: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        
        
    def get_logger(self):
        """
        returns logger
        """
        return self.logger
        