# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: __init__.py.py
@time: 2022/5/31 14:31
@description:
-------------------------------------------------
"""
import json
import requests


def http_post(url, data=None, headers=None, return_json=True):
    """
    处理 http post 请求
    :param url: api 路径
    :param data: 附带的请求数据
    :param headers: 请求头，不是必须
    :param return_json: 是否返回字典格式
    :return:
    """
    try:
        if headers is None:
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/67.0.3396.87 Safari/537.36",
            }

        if data:
            response = requests.post(url, data=json.dumps(data), headers=headers).text
        else:
            response = requests.post(url, headers=headers).text

        if return_json:
            return json.JSONDecoder().decode(response)
        return response

    except Exception as e:
        raise e


def http_get(url, data=None, headers=None, return_json=True):
    """
    处理 http post 请求
    :param url: api 路径
    :param data: 附带的请求数据
    :param headers: 请求头，不是必须
    :param return_json: 是否返回字典格式
    :return:
    """
    try:
        if headers is None:
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/67.0.3396.87 Safari/537.36",
            }

        if data:
            response = requests.get(url, data=json.dumps(data), headers=headers).text
        else:
            response = requests.get(url, headers=headers).text

        if return_json:
            return json.JSONDecoder().decode(response)
        return response
    except Exception as e:
        raise e