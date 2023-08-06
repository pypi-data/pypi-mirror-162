import pp.config as config
from pp.constants import *

#python standard libraries
import logging
import sys

#start logger
#DEBUG, INFO, WARNING, ERROR, CRITICAL
logger = logging.getLogger('pandas-plotly')
_log_config = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}  

if config.section('settings') and config.value('settings', SETTING_LOG_LEVEL):
    logger.setLevel(_log_config[config.value('settings', SETTING_LOG_LEVEL)])
else:
    logger.setLevel(logging.DEBUG)

_file_handler = logging.FileHandler(filename='tmp.log')
_stdout_handler = logging.StreamHandler(sys.stdout)
_file_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
_stdout_formatter = logging.Formatter('%(levelname)s - %(message)s')
_file_handler.setFormatter(_file_formatter)
_stdout_handler.setFormatter(_stdout_formatter)
logger.addHandler(_file_handler)
logger.addHandler(_stdout_handler)


    
