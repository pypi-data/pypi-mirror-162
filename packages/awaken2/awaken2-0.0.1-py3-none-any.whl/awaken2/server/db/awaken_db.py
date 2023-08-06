# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ Copyright 2022. quinn.7@foxmail.com All rights reserved.                 ║
# ║                                                                          ║
# ║ Licensed under the Apache License, Version 2.0 (the "License");          ║
# ║ you may not use this file except in compliance with the License.         ║
# ║ You may obtain a copy of the License at                                  ║
# ║                                                                          ║
# ║ http://www.apache.org/licenses/LICENSE-2.0                               ║
# ║                                                                          ║
# ║ Unless required by applicable law or agreed to in writing, software      ║
# ║ distributed under the License is distributed on an "AS IS" BASIS,        ║
# ║ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. ║
# ║ See the License for the specific language governing permissions and      ║
# ║ limitations under the License.                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
"""
[ Awaken 数据库 ]

"""
import sqlite3
from threading import Lock

from ...baseic.const import CONST
from ...baseic.keyword import KEYWORD
from ...baseic.error import AwakenDataBaseError
from ...baseic.decorator import singleton_pattern


@singleton_pattern
class AwakenDb(object):
    """
    [ Awaken 数据库 ]

    ---
    描述:
        基于 SQLite 数据库。

    """
    
    _conn: sqlite3.Connection = None
    """ 数据库连接对象 """
    _lock: Lock = Lock()
    """ 数据库互斥锁 """


    def __init__(self):
        """
        [ Rains 数据库 ]

        ---
        异常:
            AwakenDbInitError : Awaken 数据库初始化异常。

        """
        try:
            # 创建/连接数据库
            if not self._conn:
                self.connect()
                self._conn.commit()

        except BaseException as error:
            raise AwakenDataBaseError(error)


    def read(self, sql: str) -> list:
        """
        [ 无锁读取 ]

        ---
        描述:
            执行查询语句, 该函数不会持有数据库锁。

        ---
        参数:
            sql { str } : SQLite 查询语句。

        ---
        异常:
            AwakenDbReadError : Awaken 数据库读取异常。

        ---
        返回:
            list : 查询结果列表。

        """
        try:
            # 创建数据库游标
            cur = self._conn.cursor()
            # 执行查询语句
            cur.execute(sql)
            # 获取查询结果
            data = cur.fetchall()
            # 注销数据库游标
            cur.close()
            return data

        except BaseException as error:
            raise AwakenDataBaseError(error)


    def lock_read(self, sql: str) -> list:
        """
        [ 持锁读取 ]

        ---
        参数:
            执行查询语句, 该函数会持有数据库锁, 结束时释放。

        ---
        参数:
            sql { str } : SQLite 查询语句。

        ---
        异常:
            AwakenDbReadError : Awaken 数据库读取异常。

        ---
        返回:
            list : 查询结果列表。

        """
        # 获取锁
        with self._lock:

            # 执行读取函数
            return self.read(sql)


    def write(self, sql: str) -> int:
        """
        [ 无锁写入 ]

        描述:
            执行写入语句, 该函数不会持有数据库锁。

        ---
        参数:
            sql { str } : SQLite 查询语句。

        ---
        异常:
            AwakenDbWriteError : Awaken 数据库读取异常。

        ---
        返回:
            int : 写入数据后返回该条数据的自增ID。

        """
        try:
            # 创建数据库游标
            cur = self._conn.cursor()
            # 执行查询语句
            cur.execute(sql)
            # 获取数据自增ID
            aid = cur.lastrowid
            # 注销数据库游标
            cur.close()
            return aid

        except BaseException as error:
            raise AwakenDataBaseError(error)


    def lock_write(self, sql: str) -> int:
        """
        [ 持锁写入 ]

        ---
        描述:
            执行写入语句, 该函数会持有数据库锁, 结束时释放。

        ---
        参数:
            sql { str } : SQLite 查询语句。

        ---
        异常:
            AwakenDbWriteError : Awaken 数据库读取异常。

        ---
        返回:
            int : 写入数据后返回该条数据的自增ID。

        """
        # 获取锁
        with self._lock:

            # 执行写入函数
            return self.write(sql)


    def connect(self):
        """
        [ 数据库连接 ]

        """

        # 创建数据库连接对象
        self._conn = sqlite3.connect(CONST.Path.FilePath.Database, check_same_thread=False)

        # 创建数据库游标
        Cur = self._conn.cursor()

        # 构建数据库表
        for key, value in CreateTableSql.__dict__.items():
            if '__' in key:
                continue
            Cur.execute(value)

        # 注销数据库游标
        Cur.close()


    def commit(self):
        """
        [ 事务保存 ]

        """
        self._conn.commit()


    def rollback(self):
        """
        [ 事务回滚 ]

        """
        self._conn.rollback()


    def quit(self):
        """
        [ 关闭数据库连接 ]

        """
        self._conn.close()


class CreateTableSql(object):
    """
    [ 建表语句 ]

    """

    Tasks = f""" 

    CREATE TABLE IF NOT EXISTS { KEYWORD.DataBase.TableName.Tasks }
    (
        { KEYWORD.Api.Task.Tid }                   INTEGER PRIMARY KEY,
        { KEYWORD.Api.Task.Type }                  TEXT NOT NULL,
        { KEYWORD.Api.Task.Name }                  TEXT NOT NULL,
        { KEYWORD.Api.Task.Remark }                TEXT NOT NULL,
        { KEYWORD.Api.Task.State }                 TEXT NOT NULL,
        { KEYWORD.Api.Task.CreatedDate }           DATE NOT NULL,
        { KEYWORD.Api.Task.StartTime }             DATE,
        { KEYWORD.Api.Task.EndTime }               DATE,
        { KEYWORD.Api.Task.SpendTime }             INT,
        { KEYWORD.Api.Task.RecordCasesAll }        INT,
        { KEYWORD.Api.Task.RecordCasesSuccess }    INT,
        { KEYWORD.Api.Task.RecordCasesUnSuccess }  INT
    );

    """
    """
    [ 建表语句::任务表 ]

    """

    Cases = f"""
    
    CREATE TABLE IF NOT EXISTS { KEYWORD.DataBase.TableName.Cases }
    (
        { KEYWORD.Api.Case.Cid }          INTEGER PRIMARY KEY, 
        { KEYWORD.Api.Case.Tid }          INT  NOT NULL, 
        { KEYWORD.Api.Case.Name }         TEXT NOT NULL,
        { KEYWORD.Api.Case.Type }         TEXT NOT NULL, 
        { KEYWORD.Api.Case.Remark }       TEXT NOT NULL, 
        { KEYWORD.Api.Case.State }        TEXT NOT NULL, 
        { KEYWORD.Api.Case.CreatedDate }  DATE NOT NULL, 
        { KEYWORD.Api.Case.StartTime }    DATE,
        { KEYWORD.Api.Case.EndTime }      DATE,
        { KEYWORD.Api.Case.SpendTime }    INT,
        { KEYWORD.Api.Case.RunStep }      TEXT
    );

    """
    """
    [ 建表语句::用例表 ]

    """ 
