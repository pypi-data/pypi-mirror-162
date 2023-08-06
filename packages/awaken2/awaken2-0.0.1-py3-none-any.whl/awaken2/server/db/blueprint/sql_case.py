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
[ 任务相关SQL::用例相关 ]

"""
from ..common import get_desc_limit
from ..common import parse_case_search_criteria
from ....baseic.const import CONST
from ....baseic.keyword import KEYWORD


class SqlCase(object):
    """
    [ 任务相关SQL::用例相关 ]

    """


    @staticmethod
    def get_count(paras: dict = {}) -> str:
        """
        [ 查询用例数量 ]

        ---
        可选参数:
            tid           { int } : 任务编号
            type          { str } : 类型
            state         { str } : 状态
            created_date  { str } : 创建日期, 例如 2022-02-02

        """
        # 解析搜索条件
        where_string = parse_case_search_criteria(paras)

        return f"""

        SELECT COUNT({ KEYWORD.Api.Case.Cid }) 
        
        FROM { KEYWORD.DataBase.TableName.Cases }

        {where_string}

        """


    @staticmethod
    def get_id_list(paras: dict = {}) -> str:
        """
        [ 查询 ID 数量 ]

        ---
        可选参数:
            tid           { int } : 任务编号
            type          { str } : 类型
            state         { str } : 状态
            created_date  { str } : 创建日期, 例如 2022-02-02

        """
        # 解析搜索条件
        where_string = parse_case_search_criteria(paras)

        return f"""

        SELECT { KEYWORD.Api.Case.Cid }
        
        FROM { KEYWORD.DataBase.TableName.Cases }

        {where_string}

        ORDER BY { KEYWORD.Api.Case.Cid } DESC

        """

    @staticmethod
    def get_case_list(paras: dict = {}) -> str:
        """
        [ 查询任务所有用例详情信息列表 ]

        ---
        可选参数:
            tid           { int } : 所属任务编号
            cid           { int } : 用例编号
            type          { str } : 类型
            state         { str } : 状态
            created_date  { str } : 创建日期, 例如 2022-02-02
            page          { int } : 页数
            number        { int } : 单页数据量

        """
        # 解析搜索条件
        where_string = parse_case_search_criteria(paras)

        limit = ''
        if 'page' in paras.keys() and 'number' in paras.keys():
            limit = f"LIMIT { get_desc_limit(paras['page'], paras['number']) }"

        return f"""

        SELECT * 
        
        FROM { KEYWORD.DataBase.TableName.Cases }

        {where_string}

        ORDER BY { KEYWORD.Api.Case.Cid } DESC

        {limit}

        """


    @staticmethod
    def creation(
        tid: int,
        name: str,
        type: str,
        remark: str,
        created_date: str
    ) -> str:
        """
        [ 创建用例 ]

        ---
        参数:
            tid          { int } : 所属任务编号
            name         { str } : 用例名称
            type         { str } : 类型
            remark       { str } : 用例备注信息
            created_date { str } : 创建日期

        """
        return f""" 

        INSERT INTO { KEYWORD.DataBase.TableName.Cases } (

            { KEYWORD.Api.Case.Cid }, 
            { KEYWORD.Api.Case.Tid }, 
            { KEYWORD.Api.Case.Name },
            { KEYWORD.Api.Case.Type }, 
            { KEYWORD.Api.Case.Remark }, 
            { KEYWORD.Api.Case.State }, 
            { KEYWORD.Api.Case.CreatedDate }, 
            { KEYWORD.Api.Case.RunStep }
        )

        VALUES (

            NULL, 
            '{ tid }', 
            '{ name }',
            '{ type }',
            '{ remark }', 
            '{ CONST.State.Result.Null }', 
            '{ created_date }', 
             NULL
        )

        """


    @staticmethod
    def update(
        cid: int,
        state: str,
        start_time: str,
        end_time: str,
        spend_time: str,
        run_step: str
    ) -> str:
        """
        [ 更新用例 ]

        ---
        参数:
            cid        { int } : 用例编号
            state      { str } : 用例状态
            start_time { str } : 开始时间
            end_time   { str } : 结束时间
            spend_time { str } : 消耗时间
            run_step   { str } : 运行步骤

        """
        return f"""

        UPDATE { KEYWORD.DataBase.TableName.Cases }

        SET 
            { KEYWORD.Api.Case.State }     = "{ state }", 
            { KEYWORD.Api.Case.StartTime } = "{ start_time }", 
            { KEYWORD.Api.Case.EndTime }   = "{ end_time }", 
            { KEYWORD.Api.Case.SpendTime } = "{ spend_time }", 
            { KEYWORD.Api.Case.RunStep }   = "{ run_step }"

        WHERE
            { KEYWORD.Api.Case.Cid } = { cid }

        """


    @staticmethod
    def delete(paras: dict = {}) -> str:
        """
        [ 删除用例 ]
        
        ---
        可选参数:
            tid           { int } : 所属任务编号
            cid           { int } : 用例编号
            type          { str } : 类型
            state         { str } : 状态
            created_date  { str } : 创建日期, 例如 2022-02-02

        """
        # 解析搜索条件
        where_string = parse_case_search_criteria(paras)

        return f"""

        DELETE FROM { KEYWORD.DataBase.TableName.Cases }

        {where_string}

        """
