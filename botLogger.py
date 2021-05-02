import logging
import os
from logging import Formatter
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger(__name__)
logfile = os.path.abspath('logs/HorseBot.log')
logger.setLevel(logging.DEBUG)
fmt = Formatter('%(asctime)s %(levelname)-8s [%(file_name)-20s] %(message)s')

file_handler = TimedRotatingFileHandler(logfile, when='midnight')
file_handler.suffix = "%Y-%m-%d"
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(fmt)

stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(fmt)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
