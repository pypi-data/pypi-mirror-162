import os
import io
import sys
import re
from collections import OrderedDict as _default_dict, ChainMap as _ChainMap
import functools
from collections.abc import MutableMapping
from configuration import OnedatautilConfigParser

_SECT_TMPL = r"""
       \[                                 # [
       (?P<header>[^]]+)                  # very permissive!
       \]                                 # ]
       """
DEFAULTSECT = "DEFAULT"


def parameterized_config(template) -> str:
    """
    Generates a configuration from the provided template + variables defined in
    current scope

    :param template: a config content templated with {{variables}}
    """
    all_vars = {k: v for d in [globals(), locals()] for k, v in d.items()}
    print(globals())
    # return template.format(**all_vars)


def _parameterized_config_from_template(cfg_path) -> str:
    TEMPLATE_START = '# ----------------------- TEMPLATE BEGINS HERE -----------------------\n'

    # path = _default_config_file_path(filename)
    with open(cfg_path, encoding='utf-8') as fh:
        for line in fh:
            if line != TEMPLATE_START:
                continue
            # print(fh.read().strip())
            return fh.read().strip()
            # return parameterized_config(fh.read().strip())
    raise RuntimeError(f"Template marker not found in {cfg_path!r}")


def _default_config_file_path(file_name: str) -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates/project_template')
    # templates_dir = os.path.join(os.path.dirname(__file__), 'templates/project_template')

    return os.path.join(templates_dir, file_name)


def main():
    cfg_name = 'project.cfg'
    # dafault_cfg = 'default_airflow.cfg'
    cfg_path = _default_config_file_path(cfg_name)
    # cfg_path = os.path.join(os.path.dirname(__file__), cfg_name)

    print(cfg_path)
    cfg_data_str = _parameterized_config_from_template(cfg_path)
    #
    # cfg_data_str = os.path.join(os.path.dirname(__file__), dafault_cfg)

    local_conf = OnedatautilConfigParser(default_config=cfg_data_str)
    #
    # program_cfg_path = r'C:\Users\zhangyf\work_code\program_commons\example_demo\airflow.cfg'

    program_cfg_path = r'C:\Users\zhangyf\work_code\demo_work\barra_demo\project.cfg'
    local_conf.read(program_cfg_path, encoding='utf-8')
    print(local_conf.get("source", "request_type"))
    # print(dict(local_conf))






main()
