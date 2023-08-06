# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: setup.py.py
@time: 2022/5/31 11:23
@description:
-------------------------------------------------
"""
from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='nocode_utils',  # 包名
      version='1.2.1',  # 版本号
      description='封装常用函数和类',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='JasonHao',
      author_email='hhao9483@gmail.com',
      url='https://github.com/jasonhhao',
      install_requires=[
      ],
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      )
