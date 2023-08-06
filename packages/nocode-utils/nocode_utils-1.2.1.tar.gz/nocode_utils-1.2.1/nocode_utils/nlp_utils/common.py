# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: common.py
@time: 2022/6/20 16:35
@description:
-------------------------------------------------
"""
from nocode_utils.http_utils import http_post
import numpy as np


def get_embedding(url, sents):
    """
    得到句子向量
    :param url:
    :param sents:
    :return:
    """
    try:
        vecs = http_post(url, data={"sentences": sents}, return_json=True)['result']
        return vecs
    except Exception as e:
        raise e


def get_similarity(url, sent1, sent2):
    """
    得到两个句子的相似度
    :param url: 向量接口
    :param sent1:
    :param sent2:
    :return:
    """
    try:
        vecs = http_post(url, data={"sentences": [sent1, sent2]}, return_json=True)['result']
        vec1, vec2 = np.array(vecs[0]), np.array(vecs[1])
        return vec1.dot(vec2) / np.linalg.norm(vec1) * np.linalg.norm(vec2)
    except Exception as e:
        raise e


def get_entity(url, sent):
    """

    :param url:
    :param sent:
    :return:
    """
    try:
        res = http_post(url, data={"text": sent}, return_json=True)['data']
        return res
    except Exception as e:
        raise e

