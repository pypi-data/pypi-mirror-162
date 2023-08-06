#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : cache_utils
# @Time         : 2021/11/24 上午11:09
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://cachetools.readthedocs.io/en/stable/
"""
FIFO：First In、First Out，就是先进先出。

LFU：Least Frequently Used，就是淘汰最不常用的。

LRU：Least Recently Used，就是淘汰最久不用的。

MRU：Most Recently Used，与 LRU 相反，淘汰最近用的。

RR：Random Replacement，就是随机替换。

TTL：time-to-live 的简称，也就是说，Cache 中的每个元素都是有过期时间的，如果超过了这个时间，那这个元素就会被自动销毁。
如果都没过期并且 Cache 已经满了的话，那就会采用 LRU 置换算法来替换掉最久不用的，以此来保证数量。
"""
import pickle
import pandas as pd

from typing import Iterable
from functools import lru_cache
from joblib import Memory
from loguru import logger
from tqdm import tqdm
from cachetools import cached, cachedmethod, LRUCache, RRCache, TTLCache

# ME
from meutils.decorators import decorator


def map_cache():
    return cached({})


def ttl_cache(ttl=60, maxsize=1024):
    """https://cachetools.readthedocs.io/en/stable/

        @ttl_cache()
        @disk_cache()
        def reader():  # 多级缓存

            time.sleep(1)
    """
    return cached(TTLCache(maxsize, ttl))  # LRUCache


@decorator
def redis_cache(func, rc=None, ex=3, *args, **kwargs):
    """redis 缓存"""
    k = f"cache_{func.__name__}_{args}_{kwargs}"

    if k in rc:
        return pickle.loads(rc.get(k))
    else:
        logger.info(f"CacheKey: {k}")
        _ = func(*args, **kwargs)
        rc.set(k, pickle.dumps(_), ex=ex)
        return _


@decorator
def sqlite_cache(func, db='cache.db', verbose=False, *args, **kwargs):
    """返回值是df"""
    import sqlite3
    conn = sqlite3.connect(db)
    tables = set(pd.read_sql(f'select * from sqlite_master', conn)['tbl_name'])

    k = f"cache_{func.__name__}_{args}_{kwargs}"
    if k in tables:
        return pd.read_sql(f'select * from `{k}`', conn)
    else:
        if verbose:
            logger.info(f"CacheKey: {k}")

        df = func(*args, **kwargs)
        df.to_sql(k, conn, if_exists='replace', index=False)
        return df


@decorator
def disk_cache(func, location='cachedir', ignore=None, compress=False, verbose=0, *args, **kwargs):
    """硬盘缓存

    @param func:
    @param location:
    @param ignore: 有时我们不希望因某些参数的改变而导致重新计算，例如调试标志。
        @memory.cache(ignore=['debug'])
        def my_func(x, debug=True):
            print('Called with x = %s' % x)
    @param compress:
    @param verbose:
    @param args:
    @param kwargs:
    @return:
    """
    memory = Memory(location=location, verbose=verbose, compress=compress)
    return memory.cache(func, ignore)(*args, **kwargs)


@decorator
def cache4batch(func, location='cachedir', verbose=1, *args, **kwargs):
    """disk_cache 存中存"""

    @disk_cache(location=location)
    def wrap(batch):  # 函数最好支持 one and batch
        if isinstance(batch, Iterable) and not isinstance(batch, str):
            if verbose:
                batch = tqdm(batch, desc='miss')
            return list(map(wrap, batch))  # 递归
        return func(batch)

    return wrap(args[0])  # batch=args[0]


if __name__ == '__main__':
    from meutils.pipe import *


    @timer()
    @disk_cache(location='demo')
    def func(x):
        time.sleep(5)
        return x


    func(11)
