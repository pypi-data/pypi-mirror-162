# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: config.py
@time: 2022/7/15 17:24
@description:
-------------------------------------------------
"""
import os
from distutils.sysconfig import get_python_lib

BASE_DIR = None

if os.path.isfile(get_python_lib() + "/nocode_utils"):
  BASE_DIR = get_python_lib() + "/nocode_utils"
else:
  BASE_DIR = os.path.dirname(__file__)