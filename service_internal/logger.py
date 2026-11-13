"""
=========================================
THSI WAY I DO NOT HAVE TO ALWAYS SHOUT LOGGER IN EVERY OTHER PAGE -  THIS ONE PAGE ONLY IS ENOUGH
=========================================
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
debug_base = settings.DEBUG

def info_logger(debug = debug_base, msg = "NOT PASSED"):
    "Info / Debug Logger"
    if debug: print(msg)
    else: return logger.info(msg=msg)
    
def warning_logger(debug = debug_base, msg = "NOT PASSED"):
    "Warning / Debug Logger"
    if debug: print(msg)
    else: return logger.warning(msg=msg)

def error_logger(debug = debug_base, msg = "NOT PASSED"):
    "Error / Debug Logger"
    if debug: print(msg)
    else: return logger.error(msg=msg)

