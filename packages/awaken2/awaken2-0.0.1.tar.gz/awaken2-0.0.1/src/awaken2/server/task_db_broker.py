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
[ 任务数据库代理 ]

"""
import time

from .db import DB
from .db import SQL
from ..baseic.const import CONST


class TaskDbBroker: ...


class TaskDbBroker:
    """
    [ 任务数据库代理 ]

    ---
    描述:
        该类将代理任务执行过程中的数据库写入事务。

    """

    _task_type: str
    """ 任务类型 """
    _task_id: int
    """ 任务ID """
    _task_created_date: str
    """ 任务创建日期 """
    _task_start_time: str
    """ 任务开始时间 """
    _task_start_timestamp: int
    """ 任务开始时间戳 """
    _record_cases_all: int
    """ 统计所有用例数 """
    _record_cases_success: int
    """ 统计成功用例数 """
    _record_cases_unsuccess: int
    """ 统计失败用例数 """


    def __init__(self, task_type: str):
        """
        [ 任务外交代理 ]
        
        ---
        参数:
            task_type { str } : 任务类型
        
        """
        self._record_cases_all = 0
        self._record_cases_success = 0
        self._record_cases_unsuccess = 0
        self._task_type = task_type


    def task_start(self, name: str, remark: str) -> int:
        """
        [ 任务开始 ]

        ---
        参数:
            name   { str } : 任务名称
            remark { str } : 任务注释

        ---
        返回:
            int : 创建的任务数据库记录ID
        
        """
        # 记录任务开始时间
        self._task_created_date = time.strftime('%Y-%m-%d')
        self._task_start_time = time.strftime('%H:%M:%S')
        self._task_start_timestamp = int(time.time())

        # 录入数据库任务记录
        self._task_id = DB.write(SQL.Task.creation(
            self._task_type,
            name,
            remark, 
            self._task_created_date,
        ))

        return self._task_id


    def created_case(self, name: str, remark: str) -> int:
        """
        [ 创建用例 ]

        ---
        参数:
            name   { str } : 用例名称
            remark { str } : 用例注释

        ---
        返回:
            int : 创建的用例数据库记录ID

        """
        # 录入数据库用例记录
        case_id = DB.write(SQL.Case.creation(
            self._task_id,
            name,
            self._task_type,
            remark,
            self._task_created_date
        ))
        self._record_cases_all += 1

        return case_id


    def update_case(
        self, 
        cid: int, 
        state: str, 
        start_time: str, 
        start_timestamp: int, 
        run_step: str
    ):
        """
        [ 更新用例 ]
        
        ---
        参数:
            cid             { int } : 用例ID
            state           { str } : 用例状态
            start_time      { str } : 开始时间
            start_timestamp { int } : 开始时间戳
            run_step        { str } : 执行步骤

        """
        # 录入数据库更新用例
        DB.write(SQL.Case.update(
            cid,
            state,
            start_time,
            time.strftime('%H:%M:%S'),
            (int(time.time()) - start_timestamp),
            run_step
        ))

        if state == CONST.State.Result.Success:
            self._record_cases_success += 1

        if state == CONST.State.Result.Unsuccess:
            self._record_cases_unsuccess += 1

        if state == CONST.State.Result.Error:
            self._record_cases_unsuccess += 1


    def task_end(self, state: str):
        """
        [ 任务结束 ]

        ---
        参数:
            state { str } : 任务状态

        """
        # 更新数据库任务记录
        DB.write(SQL.Task.update(
            self._task_id,
            state,
            self._task_start_time,
            time.strftime('%H:%M:%S'),
            (int(time.time()) - self._task_start_timestamp),
            self._record_cases_all,
            self._record_cases_success,
            self._record_cases_unsuccess
        ))

        # 保存事务
        DB.commit()
