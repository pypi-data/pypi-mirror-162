import os

import example_demo.setting as setting

class BaseUrlSource(object):

    def init_setting_source(self):

        pass

    def parse_setting_url(self):

        pass

    @property
    def name(self):
        return self.__class__.__name__

    def close(self):
        pass

