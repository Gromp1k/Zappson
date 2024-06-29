import logging

class ZLogger(logging.Logger):
    def __init__(self, name: str, log_file: str, level=logging.INFO):
        super().__init__(name, level)

        # Setting up a FileHandler for this logger
        handler = logging.FileHandler(log_file)
        handler.setLevel(level)

        # Defining the logging format
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)

        # Adding the handler to the logger
        self.addHandler(handler)

# Creating a logger instance using the custom ZLogger class
logger = ZLogger(__name__, 'module.log')

# Example log message
logger.info('This is a log message from the module')
