# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: Threads.py
@time: 2022/5/31 14:59
@description:
-------------------------------------------------
"""
import threading



class Threads(threading.Thread):

    def __init__(self,func,args=()):
        """
        线程实例，每个线程一个实例
        使用方法参考：
            myThread = Threads(foo, args=(data, 'hello', 'world'))
            result = myThread.get_result()
        :param func: 要执行的函数
        :param args: 传给函数的参数，可以是任意结构
        """
        super(Threads,self).__init__()
        self.result = None
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        """
        线程执行所拿到的返回值
        :return:
        """
        try:
            return self.result
        except Exception as e:
            raise Exception(e)