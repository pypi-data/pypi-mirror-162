#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : path_utils
# @Time         : 2020/11/12 11:39 上午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  : 

import os
import sys
import json
import yaml

from pathlib import Path
from loguru import logger

get_module_path = lambda path, file=__file__: \
    os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(file), path))

get_resolve_path = lambda path, file=__file__: (Path(file).parent / Path(path)).resolve()


def file2json(path):
    p = Path(path)

    o = {}
    if p.is_file():

        if p.name.endswith('.json'):
            o = json.loads(p.read_bytes())

        elif p.name.endswith('.yaml') or p.name.endswith('.yml'):
            o = yaml.safe_load(p.read_bytes())
    else:
        logger.error(f"无效地址：{path}")
    return o


def sys_path_append(path, __file__=None):
    """添加home到系统
    """
    if __file__:
        path = get_module_path(path, __file__)

    p = Path(path).resolve()
    if p.is_file():
        py_home = p.parent.__str__()
    elif p.is_dir():
        py_home = p.__str__()
    else:
        raise Exception(f"{path} 为错误路径")

    logger.info(f"{path} HOME: {py_home}")

    sys.path.append(py_home)

    return py_home


def path2list(path, pattern='*'):
    ps = []
    p = Path(path)
    if p.is_file():
        ps = [p]
    elif p.is_dir():
        ps = list(p.glob(pattern))
    else:
        logger.error('ErrorPath !!!')
    return ps


def get_config(config_init=None):
    if isinstance(config_init, str) and Path(config_init).is_file():
        p = Path(config_init)

        if p.name.endswith('.json'):
            config_init = json.loads(p.read_bytes())

        elif p.name.endswith('.yaml') or p.name.endswith('.yml'):
            config_init = yaml.safe_load(p.read_bytes())

        else:
            logger.error('目前只支持dict/json/yaml格式')
            config_init = {}

    else:
        config_init = config_init if config_init else {}

    return config_init


if __name__ == '__main__':
    print(os.getcwd())
    print(os.path.dirname(__file__))
