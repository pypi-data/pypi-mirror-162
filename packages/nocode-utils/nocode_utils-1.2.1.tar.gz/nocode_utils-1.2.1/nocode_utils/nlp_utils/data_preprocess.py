# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: data_preprocess.py
@time: 2022/5/31 14:45
@description:
-------------------------------------------------
"""
import re


def is_all_chinese(sent):
    """
    判断一个句子是否全是中文
    :param sent:
    :return:
    """
    for _char in sent:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


def is_contains_chinese(sent):
    """
    判断一个句子是否包含中文
    :param sent:
    :return:
    """
    for _char in sent:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def is_contains_english(sent):
    """
    判断一个句子是否包含英文字符
    :param sent:
    :return:
    """
    for char in sent:
        if char in "qwertyuioplkjhgfdsazxcvbnm":
            return True
    return False


def only_keep_chinese(sent):
    return re.sub('[^\u4e00-\u9fa5]+', '', sent)


def get_sentence_num(doc, sep='。，！？；'):
    """
    得到文本句子个数，默认以 [。，！？；] 为句子分割
    :param doc: 文本，无最长限制
    :param sep: 分割符
    :return: 句子个数，所有句子
    """

    for s in sep:
        doc = doc.replace(s, "$$$")

    count = 0
    sens = []
    for sen in doc.split("$$$"):
        if len(sen) > 0:
            count += 1
            sens.append(sen)

    return count, sens


