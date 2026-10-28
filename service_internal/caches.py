"""
==========================================
HANDLING CENTRALIZED CACHE SETTINGS THAT IS REUSABLE
==========================================
"""
from .logger import info_logger
from django.core.cache import cache

def set_cache(key, value, timeout = None):
    info_logger(msg=f"CACHE-SET: Set Cache for {key} to a timeout of {timeout}")
    cache.set(key, value, timeout)
    return 0

def get_cache(key):
    value = cache.get(key)
    if not value:
        info_logger(msg=f"CACHE-GET: No Cache Was Found With the key ({key})")
        return False
    return value

def del_cache(key):
    success = cache.delete(key)
    if success:
        info_logger(msg=f"CACHE-DELETE: The cache with the key :{key} have been deleted successfuly")
        return False
    else:
        info_logger(msg=f"CACHE-DELETE: Failed to delete the cache with the key {key}")
        return False