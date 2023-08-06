# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: DBProcessor.py
@time: 2022/5/31 14:20
@description:
-------------------------------------------------
"""

from DBUtils.PooledDB import PooledDB


class DBProcessor(object):

    def __init__(self, type, database, user, password, host, port, conn_min=5, conn_max=30, timeout=60):
        '''
        初始化数据库处理器
        :param type: 数据库名称（仅支持 PostgreSQL 或者 MySQL）
        :param database: 数据库名称
        :param user: 用户名
        :param password: 密码
        :param host: 主机
        :param port: 端口
        :param conn_min: 连接池最小连接数
        :param conn_max: 连接池最大连接数
        '''

        self.type = type
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self._pool = None
        self.conn_min = conn_min
        self.conn_max = conn_max
        self.timeout = timeout

    def init_pool(self):
        if self.type == 'PostgreSQL':
            import psycopg2 as pscg
            self._pool = PooledDB(pscg, mincached=self.conn_min, maxcached=self.conn_max,
                                  blocking=True, user=self.user,
                                  password=self.password, database=self.database,
                                  host=self.host, port=self.port, connect_timeout=self.timeout)
        elif self.type == 'MySQL':
            import pymysql
            self._pool = PooledDB(pymysql, mincached=self.conn_min, maxcached=self.conn_max,
                                  blocking=True, user=self.user,
                                  password=self.password, database=self.database,
                                  host=self.host, port=self.port, connect_timeout=self.timeout)

    def get_pool_conn(self):
        if not self._pool:
            self.init_pool()
        return self._pool.connection()

    def execute_sql(self, sql, values=None, ret=False):
        '''
        执行 sql 语句
        :param sql: sql 语句
        :param values: sql 语句中的变量
        :param ret: 是否有返回值
        :return:
        '''

        try:
            res = None
            conn = self.get_pool_conn()

            cur = conn.cursor()
            if values is None:
                cur.execute(sql)
            else:
                cur.execute(sql, values)
            if ret:
                res = cur.fetchall()
            if ret:
                return res

        except Exception as e:
            raise Exception(e)
        finally:
            conn.commit()
            cur.close()
            conn.close()
