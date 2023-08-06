# -*- coding: utf-8 -*-
import redis
import json
import example_demo.setting as setting
import logging as log

def connect_redis(db, host=None, port=None, password=None):
    host = host or setting.REDIS_HOST
    port = port or setting.REDIS_PORT
    # db = db or setting.EMAIL_FROM
    password = password or setting.REDIS_PASSWORD
    connection_pool = redis.ConnectionPool(host=host,
                                           port=port,
                                           db=db,
                                           password=password)
    redis_client = redis.Redis(connection_pool=connection_pool)

    return redis_client


def get_proxy_from_redis(proxy_db=None):
    proxy_db = proxy_db or setting.REDIS_PROXY_DB
    redis_client = connect_redis(proxy_db)

    proxies = json.loads((redis_client.randomkey()))
    redis_client.close()
    return proxies


from tenacity import (
    retry,
    retry_if_exception_type,
    wait_random_exponential,
    before_sleep_log
)

RETRY_EXCEPTIONS = (
    redis.exceptions.ConnectionError,
    redis.exceptions.ResponseError,
    redis.exceptions.TimeoutError,
)

auto_retry = retry(
    retry=retry_if_exception_type(RETRY_EXCEPTIONS),
    wait=wait_random_exponential(multiplier=1, max=4),
    before_sleep=before_sleep_log(log, log.WARN),
    reraise=True
)


class RetryRedis(object):
    def __init__(self, url):
        self._url = url
        self._redis = None

    @property
    def r(self):
        if not self._redis:
            self._redis = redis.from_url(self._url)
        return self._redis

    def __repr__(self):
        return "%s<%s>" % (type(self).__name__, repr(self._redis))

    def __getattr__(self, key):
        def fn(*args, **kwargs):
            try:
                redis_method = getattr(self.r, key)
                return redis_method(*args, **kwargs)
            except RETRY_EXCEPTIONS:
                self._redis = None
                raise

        return auto_retry(fn)


def from_url(url):
    return RetryRedis(url)


__all__ = ["from_url", "auto_retry"]
