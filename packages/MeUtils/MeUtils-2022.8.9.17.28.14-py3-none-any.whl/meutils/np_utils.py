#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : np_utils
# @Time         : 2020/11/12 11:35 上午
# @Author       : yuanjie
# @Email        : meutils@qq.com
# @Software     : PyCharm
# @Description  : 

from sklearn.metrics.pairwise import cosine_similarity

# ME
from meutils.pipe import *

# 分组
# np.array_split(range(6), 3)
# iteration_utilities.split
# iteration_utilities.grouper([1,2,3,4], 2) | xlist


# 展平
"""
l=[[1,2,3],[4,[5],[6,7]],[8,[9,[10]]]]*1000
from iteration_utilities import deepflatten
_ = list(deepflatten(l)) # 快十倍
_ = sum(l, [])
"""


def normalize(x):
    if len(x.shape) > 1:
        return x / np.clip(x ** 2, 1e-12, None).sum(axis=1).reshape((-1, 1) + x.shape[2:]) ** 0.5
    else:
        return x / np.clip(x ** 2, 1e-12, None).sum() ** 0.5


def cosine(v1, v2):  # 相似度不是距离
    """
    v1 = np.array([[1, 2], [3, 4]])
    v2 = np.array([[5, 6], [7, 8], [5, 6]])
    cosine_dist(v1, v2)
    """
    assert v1.ndim == v2.ndim
    if v1.ndim == 1:
        v1, v2 = v1.reshape(1, -1), v2.reshape(1, -1)
    return cosine_similarity(v1, v2).clip(0, 1)

def cosine_topk(v1, v2, topk=10):  # 相似度不是距离
    dist = - cosine(v1, v2)
    idxs = np.argsort(dist)[:, :topk]
    scores = - np.take_along_axis(dist, idxs, -1)  # 取出得分
    return idxs, scores


def get_sorted_top_k(array, top_k=1, axis=-1, reverse=False):
    """https://blog.csdn.net/danengbinggan33/article/details/112525700
    多维数组排序
    Args:
        array: 多维数组
        top_k: 取数
        axis: 轴维度
        reverse: 是否倒序

    Returns:
        top_sorted_scores: 值
        top_sorted_indexes: 位置
    """
    if reverse:
        # argpartition分区排序，在给定轴上找到最小的值对应的idx，partition同理找对应的值
        # kth表示在前的较小值的个数，带来的问题是排序后的结果两个分区间是仍然是无序的
        # kth绝对值越小，分区排序效果越明显
        axis_length = array.shape[axis]
        partition_index = np.take(np.argpartition(array, kth=-top_k, axis=axis),
                                  range(axis_length - top_k, axis_length), axis)
    else:
        partition_index = np.take(np.argpartition(array, kth=top_k, axis=axis), range(0, top_k), axis)
    top_scores = np.take_along_axis(array, partition_index, axis)
    # 分区后重新排序
    sorted_index = np.argsort(top_scores, axis=axis)
    if reverse:
        sorted_index = np.flip(sorted_index, axis=axis)
    top_sorted_scores = np.take_along_axis(top_scores, sorted_index, axis)
    top_sorted_indexes = np.take_along_axis(partition_index, sorted_index, axis)
    return top_sorted_indexes, top_sorted_scores


if __name__ == "__main__":
    import time
    from sklearn.metrics.pairwise import cosine_similarity

    x = np.random.rand(10, 128)
    y = np.random.rand(1000000, 128)
    z = cosine_similarity(x, y)

    start_time = time.time()
    sorted_index_1 = get_topk_index_(z, topk=3, axis=1)[1]
    print(time.time() - start_time)

    start_time = time.time()
    sorted_index_2 = np.flip(np.argsort(z, axis=1)[:, -3:], axis=1)
    print(time.time() - start_time)

    print((sorted_index_1 == sorted_index_2).all())
