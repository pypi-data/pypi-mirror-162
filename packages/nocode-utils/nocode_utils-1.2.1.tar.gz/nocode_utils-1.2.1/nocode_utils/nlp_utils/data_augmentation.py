# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: data_augmentation.py
@time: 2022/7/15 14:00
@description:
-------------------------------------------------
"""
import numpy as np
import hashlib


def random_word(text, num=10):
    from nlpcda import Randomword
    """
    随机(等价)实体替换
    :param text:
    :param num:
    :return:
    """
    smw = Randomword(create_num=num + 1)
    return smw.replace(text)[1:]


def similar_word(text, num=10):
    from nlpcda import Similarword
    """
    随机同义词替换
    :param text:
    :param num:
    :return:
    """
    smw = Similarword(create_num=num + 1)
    return smw.replace(text)[1:]


def homophone(text, num=10):
    from nlpcda import Homophone
    """
    随机近义字替换
    :param text:
    :param num:
    :return:
    """
    smw = Homophone(create_num=num + 1)
    return smw.replace(text)[1:]


def char_position_exchange(text, char_gram=3, num=10):
    from nlpcda import CharPositionExchange
    """
    随机置换邻近的字
    :param text:
    :param num:
    :return:
    """
    smw = CharPositionExchange(create_num=num + 1, char_gram=char_gram, seed=1)
    return smw.replace(text)[1:]


def equivalent_char(text, num=10):
    from nlpcda import EquivalentChar
    """
    等价字替换
    :param text:
    :param num:
    :return:
    """
    smw = EquivalentChar(create_num=num + 1)
    return smw.replace(text)[1:]


def random_delete_char(text, change_rate=0.3, num=10):
    """

    :param text: 随机字删除
    :param num:
    :param change_rate: 文本改变率
    :return:
    """
    from nlpcda import RandomDeleteChar
    smw = RandomDeleteChar(create_num=num + 1, change_rate=change_rate)
    return smw.replace(text)[1:]


def baidu_translate(text, appid, secretKey, t_from, t_to, medical=False):
    """
    百度翻译接口
    :param medical: 是否为医学领域
    :param text: 文本
    :param appid:
    :param secretKey:
    :param t_from: 当前语种
    :param t_to: 目标语种
    :return:
    """
    from nocode_utils.http_utils import http_get

    if medical:
        str1 = f"{appid}{text}1435660288medicine{secretKey}"
        sign = hashlib.md5(str1.encode('utf-8')).hexdigest()
        url = f"http://api.fanyi.baidu.com/api/trans/vip/fieldtranslate?q={text}&from={t_from}&to={t_to}&appid={appid}&salt=1435660288&domain=medicine&sign={sign}"
    else:
        str1 = f"{appid}{text}1435660288{secretKey}"
        sign = hashlib.md5(str1.encode('utf-8')).hexdigest()
        url = f"http://api.fanyi.baidu.com/api/trans/vip/translate?q={text}&from={t_from}&to={t_to}&appid={appid}&salt=1435660288&sign={sign}"

    res = http_get(url=url)
    try:
        return res['trans_result'][0]['dst']
    except:
        return res


