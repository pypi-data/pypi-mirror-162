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
[ 任务相关SQL::任务相关 ]

"""
from ..common import get_desc_limit
from ..common import parse_task_search_criteria
from ....baseic.const import CONST
from ....baseic.keyword import KEYWORD


class SqlTask(object):
    """
    [ 任务相关SQL::任务相关 ]

    """


    @staticmethod
    def get_count(paras: dict = {}) -> str:
        """
        [ 查询任务数量 ]

        ---
        可选参数:
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        return f"""

        SELECT COUNT({ KEYWORD.Api.Task.Tid })

        FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        """


    @staticmethod
    def get_id_list(paras: dict = {}) -> str:
        """
        [ 查询 ID 列表 ]

        ---
        可选参数:
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        return f"""

        SELECT { KEYWORD.Api.Task.Tid }

        FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        ORDER BY { KEYWORD.Api.Task.Tid } DESC

        """


    @staticmethod
    def get_exist_task_dates(paras: dict = {}) -> str:
        """
        [ 查询去重后的所有存在任务的日期列表 ]

        ---
        可选参数:
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        return f"""

        SELECT DISTINCT { KEYWORD.Api.Task.CreatedDate } 

        FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        ORDER BY { KEYWORD.Api.Task.Tid } DESC

        """


    @staticmethod
    def get_spend_time(paras: dict = {}) -> str:
        """
        [ 查询任务的消耗时间 ]

        ---
        可选参数:
            tid                 { int } : 任务编号
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        return f""" 

        SELECT SUM({ KEYWORD.Api.Task.SpendTime })

        FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        """


    @staticmethod
    def get_task_list(paras: dict = {}) -> str:
        """
        [ 查询任务列表 ]

        ---
        可选参数:
            tid                 { int } : 任务编号
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常
            page                { int } : 页数
            number              { int } : 单页数据量

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        limit = ''
        if 'page' in paras.keys() and 'number' in paras.keys():
            limit = f"LIMIT { get_desc_limit(paras['page'], paras['number']) }"

        return f"""

        SELECT * 

        FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        ORDER BY { KEYWORD.Api.Task.Tid } DESC

        {limit}

        """


    @staticmethod
    def creation(
        type: str,
        name: str,
        remark: str,
        created_date: str
    ) -> str:
        """
        [ 创建任务 ]

        ---
        参数:
            type         { str } : 任务类型
            name         { str } : 任务名称
            remark       { str } : 任务备注
            created_date { str } : 创建日期, 例如 2022-02-02

        """
        return f""" 

        INSERT INTO { KEYWORD.DataBase.TableName.Tasks } (

            { KEYWORD.Api.Task.Tid },
            { KEYWORD.Api.Task.Type },
            { KEYWORD.Api.Task.Name },
            { KEYWORD.Api.Task.Remark }, 
            { KEYWORD.Api.Task.State }, 
            { KEYWORD.Api.Task.CreatedDate }, 
            { KEYWORD.Api.Task.StartTime }, 
            { KEYWORD.Api.Task.EndTime }, 
            { KEYWORD.Api.Task.SpendTime }, 
            { KEYWORD.Api.Task.RecordCasesAll }, 
            { KEYWORD.Api.Task.RecordCasesSuccess }, 
            { KEYWORD.Api.Task.RecordCasesUnSuccess }
        )

        VALUES (

            NULL,
            '{ type }',
            '{ name }',
            '{ remark }',
            '{ CONST.State.Result.Null }',
            '{ created_date }',
            NULL, NULL, NULL, NULL, NULL, NULL
        )

        """


    @staticmethod
    def update(
        tid: int,
        state: str,
        start_time: str,
        end_time: str,
        spend_time: int,
        record_cases_all: int,
        record_cases_success: int,
        record_cases_unsuccess: int
    ) -> str:
        """
        [ 更新任务 ]

        ---
        参数:
            tid                    { int } : 任务编号
            state                  { str } : 任务状态
            start_time             { str } : 开始时间
            end_time               { str } : 结束时间
            spend_time             { int } : 消耗时间
            record_cases_all       { int } : 统计所有用例数
            record_cases_success   { int } : 统计成功用例数
            record_cases_unsuccess { int } : 统计成功用例数

        """
        return f"""

        UPDATE { KEYWORD.DataBase.TableName.Tasks }

        SET
            { KEYWORD.Api.Task.State }                 = '{ state }', 
            { KEYWORD.Api.Task.StartTime }             = '{ start_time }', 
            { KEYWORD.Api.Task.EndTime }               = '{ end_time }', 
            { KEYWORD.Api.Task.SpendTime }             = '{ spend_time }', 
            { KEYWORD.Api.Task.RecordCasesAll }        =  { record_cases_all }, 
            { KEYWORD.Api.Task.RecordCasesSuccess }    =  { record_cases_success }, 
            { KEYWORD.Api.Task.RecordCasesUnSuccess }  =  { record_cases_unsuccess }

        WHERE 
            { KEYWORD.Api.Task.Tid } = { tid }

        """


    @staticmethod
    def delete(paras: dict = {}) -> str:
        """
        [ 删除任务 ]

        ---
        可选参数:
            tid                 { int } : 任务编号
            type                { str } : 类型
            state               { str } : 状态
            created_date        { str } : 创建日期, 例如 2022-02-02
            record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

        """
        # 解析搜索条件
        where_string = parse_task_search_criteria(paras)

        return f"""

        DELETE FROM { KEYWORD.DataBase.TableName.Tasks }

        {where_string}

        """
