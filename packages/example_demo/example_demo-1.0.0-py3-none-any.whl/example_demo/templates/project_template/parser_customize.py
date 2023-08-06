# -*- coding: utf-8 -*-
import os
# from onedatautil.commons.common_fun import check_path
from example_demo.commons.common_fun import check_path

import datetime
# import onedatautil.setting as setting
import example_demo.setting as setting
import json
import math
from example_demo.monitor.monitor_signal_alert import send_mail


class ParseCustomize():
    def __init__(self):
        # self.final_result = ''
        # self.count = 0
        self.parse_customize_enable = False
        self.final_parse_enable = False
        pass

    def parse_customize_one(self, content, url_source, **kwargs):
        pass

    def final_parse(self, url_source):
        pass
