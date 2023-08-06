# -*- coding: UTF-8 -*-
import configparser


class ParseConfIni(configparser.ConfigParser):
    def __init__(self, need_transform=False):
        super().__init__()
        self.need_transform = need_transform

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d


def get_cfg_data(cfg_file, need_dict=False):
    config = ParseConfIni()
    try:
        config.read(cfg_file, encoding="utf-8-sig")
    except Exception as e:
        config.read(cfg_file)

    return config if not need_dict else config.as_dict()
