#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : common
# @Time         : 2021/9/10 上午10:45
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

import os
import sys
import schedule
import threading
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# ME
from meutils.decorators.decorator import decorator


@contextmanager
def timer(task="Task"):
    """https://www.kaggle.com/lopuhin/mercari-golf-0-3875-cv-in-75-loc-1900-s
        # 其他装饰器可学习这种写法
        with timer() as t:
            time.sleep(3)

        @timer()
        def f():
            print('sleeping')
            time.sleep(6)
            return 6
    """

    logger.info(f"{task} started")
    s = time.time()
    yield
    e = time.time()
    logger.info(f"{task} done in {e - s:.3f} s")


@decorator
def do_nothing(func, *args, **kwargs):
    return func(*args, **kwargs)


@decorator
def timeout(func, seconds=1, *args, **kwargs):
    future = ThreadPoolExecutor(1).submit(func, *args, **kwargs)
    return future.result(timeout=seconds)


@decorator
def fork(task, *args, **kwargs):
    """
    def task():
        logger.info(f"task进程：{os.getpid()}")

        for i in range(10) | xtqdm:
            time.sleep(1)
    fork(task)()
    """
    logger.info(f"父进程：{os.getppid()}")

    pid = os.fork()

    if pid < 0:
        logger.error("子进程建立失败")
    elif pid == 0:  # 在子进程中的返回值
        task(*args, **kwargs)
        logger.info(f"{task.__name__} 进程：{os.getpid()}")
    else:  # 在父进程中的返回值
        task(*args, **kwargs)
        logger.info(f"{task.__name__} 进程：{os.getpid()}")


@decorator
def pylock(func, lock=threading.Lock(), *args, **kwargs):
    """https://baijiahao.baidu.com/s?id=1714105650396326932&wfr=spider&for=pc"""
    with lock:
        # lock.acquire()
        _ = func(*args, **kwargs)
        # lock.release()
        return _


@decorator
def timeout(func, seconds=1, *args, **kwargs):
    future = ThreadPoolExecutor(1).submit(func, *args, **kwargs)
    return future.result(timeout=seconds)


@decorator
def backend(func, *args, **kwargs):
    """
        @backend
        def func(x):
            import time
            print(time.time())
            time.sleep(3)
            print(time.time())

        @backend
        def func():
            global d
            d = {}
            while 1:
                import time
                time.sleep(3)
                d['t'] = time.ctime() # 后台更新全局变量

    @param func:
    @param args:
    @param kwargs:
    @return:
    """
    pool = ThreadPoolExecutor(1)
    future = pool.submit(func, *args, **kwargs)
    return future.running()  # future.done()


# @backend
@decorator
def scheduler(func, scheduler_=schedule.every(2).seconds, stop_func=lambda: False, *args, **kwargs):
    """设置调度的参数，这里是每2秒执行一次

        t = time.time() + 10
        def f():
            time.sleep(1)
            return time.time() > t


        @scheduler(stop_func=f)
        def job(arg):
            print(f"{arg}: a simple scheduler in python.")

        @backend
        @scheduler(stop_func=lambda: False)
        def job():
            global d
            d = {}
            d['t'] = time.ctime() # 后台更新全局变量

    :param func:
    :param scheduler_:
    :param stop_func:
    :param args:
    :param kwargs:
    :return:
    """
    # 先初始化一次
    logger.info(f"{func.__name__} 调度初始化: {func(*args, **kwargs)}")

    # 正式调度
    scheduler_.do(func, *args, **kwargs)

    while True:
        schedule.run_pending()

        if stop_func():
            logger.info(f"{func.__name__} 调度终止")
            break


if __name__ == '__main__':
    import time


    @timeout()
    def ff():
        import time
        time.sleep(30)
        return "OK"


    print(ff())
    #
    #
    # def func():
    #     print(f"开始循环: {time.time()}")
    #     for i in range(10):
    #         time.sleep(1)
    #         print(f"{i}: {time.time()}")
    #
    #
    # @do_more(do_more_func=func)
    # def func_main():
    #     return "hhh"
    #
    #
    # print(func_main())
    # #
    # #
    #
    # def _do_more():
    #     print(f"开始: {time.time()}")
    #     executor = ThreadPoolExecutor(1)
    #     future = executor.submit(func)
    #
    #     # 主逻辑
    #     print(f"结束: {time.time()}")
    #
    #     return "do_more"
    #
    #
    # print(_do_more())
