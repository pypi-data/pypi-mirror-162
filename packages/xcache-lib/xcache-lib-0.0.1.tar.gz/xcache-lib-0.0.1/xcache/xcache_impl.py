# -*- coding: utf-8 -*-

"""
Authors:
    chuanqi.tan ### gmail.com

XCache: A simplest and thread-safe LRU cache, which support key-func, release-func and hit-stat.

Features:
    - LRU cache
    - Thread safe
    - Support special key function
    - Support special release function
    - Has detail hit stat
"""

from collections import OrderedDict, defaultdict
from functools import wraps
import threading


class XCache(object):
    def __init__(
        self, cache_size, get_func, key_func=None, release_func=None, log_keys=False
    ):
        self.cache_size = cache_size
        self.get_func = get_func
        self.key_func = key_func
        self.release_func = release_func

        self._cache = OrderedDict()
        self._lock = threading.Lock()

        self._log_keys = log_keys
        self._hit_stat = [0, 0]
        if self._log_keys:
            self._hit_detail = defaultdict(int)
            self._key_detail = defaultdict(int)

    def __call__(self, *args):
        if self.key_func:
            key = self.key_func(*args)
        else:
            key = tuple(args)

        try:
            with self._lock:
                value = self._cache.pop(key)
                self._cache[key] = value

                self._hit_stat[0] += 1
                if self._log_keys:
                    self._hit_detail[key] += 1
                    self._key_detail[key] += 1
                return value
        except KeyError:
            pass

        value = self.get_func(*args)

        try:
            with self._lock:
                if len(self._cache) >= self.cache_size:
                    _, v = self._cache.popitem(last=False)
                    if self.release_func:
                        self.release_func(v)

                self._cache[key] = value
                self._hit_stat[1] += 1
                if self._log_keys:
                    self._key_detail[key] += 1
        except ValueError:
            pass  # large value

        return value


def xcache(cache_size, key_func=None, release_func=None, log_keys=False):
    def _xcache_inner1(get_func):
        x = XCache(cache_size, get_func, key_func, release_func, log_keys)
        get_func.__xcache__ = x

        @wraps(get_func)
        def _xcache_inner2(*args, **kwargs):
            return x(*args, **kwargs)

        return _xcache_inner2

    return _xcache_inner1


def __calc_percentage_of_detail(detail):
    detail_num = defaultdict(int)
    for _, v in detail.items():
        detail_num[v] += 1

    return detail_num


def show_xcache_hit_stat(func):
    cacher = func.__xcache__
    stat = {
        "hit": cacher._hit_stat,
    }
    total = sum(cacher._hit_stat)
    if total > 0:
        stat["hit_rate"] = cacher._hit_stat[0] * 100.0 / sum(cacher._hit_stat)
    else:
        stat["hit_rate"] = 0

    if hasattr(cacher, "_hit_detail"):
        stat["keys_num"] = len(cacher._hit_detail)
        stat["detail"] = {
            "hit_detail": __calc_percentage_of_detail(cacher._hit_detail),
            "key_detail": __calc_percentage_of_detail(cacher._key_detail),
        }

        if total > 0:
            stat["dup_calc_rate"] = (stat["hit"][1] - stat["keys_num"]) * 1.0 / total
        else:
            stat["dup_calc_rate"] = 0

    return stat
