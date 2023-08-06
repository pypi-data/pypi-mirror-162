# -*- coding: utf-8 -*-
import traceback
import time
from example_demo.request_downloader.downloaders import get_request_content, get_random_ua
import example_demo.commons.common_fun as common
import datetime

import example_demo.setting as setting
from example_demo.utils.redis_client import get_proxy_from_redis


class RequestProcess():

    def __init__(self, request_info,  debug=False, **kwargs):
        self.request_info = request_info
        self.debug = debug

    def request_get_res(self):
        if setting.REDIS_PROXY_DB and not self.request_info.get("proxies"):
            self.request_info["proxies"] = get_proxy_from_redis()
        if setting.SOURCE_NEED_UA and not common.try_get(self.request_info, ["headers", "User-Agent"]):
            if not self.request_info.get("headers"):
                self.request_info["headers"] = {}
            self.request_info["headers"]["User-Agent"] = get_random_ua()
        self.request_info["debug"] = self.debug
        if self.debug:
            print(self.request_info)
        res = get_request_content(**self.request_info)
        return res


