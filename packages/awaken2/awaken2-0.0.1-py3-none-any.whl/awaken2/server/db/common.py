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
[ 数据库模块通用函数 ]

"""
from ...baseic.keyword import KEYWORD


def parse_task_search_criteria(paras: dict):
    """
    [ 解析任务搜索条件 ]
    
    """
    where_list = []
    paras_keys = paras.keys()
    if KEYWORD.Api.Task.Tid in paras_keys:
        where_list.append(f'{KEYWORD.Api.Task.Tid} = {paras[KEYWORD.Api.Task.Tid]}')
    if KEYWORD.Api.Task.Type in paras_keys:
        where_list.append(f'{KEYWORD.Api.Task.Type} = "{paras[KEYWORD.Api.Task.Type]}"')
    if KEYWORD.Api.Task.Name in paras_keys:
        where_list.append(f'{KEYWORD.Api.Task.Name} = "{paras[KEYWORD.Api.Task.Name]}"')
    if KEYWORD.Api.Task.State in paras_keys:
        where_list.append(f'{KEYWORD.Api.Task.State} = "{paras[KEYWORD.Api.Task.State]}"')
    if KEYWORD.Api.Task.CreatedDate in paras_keys:
        where_list.append(f'{KEYWORD.Api.Task.CreatedDate} = "{paras[KEYWORD.Api.Task.CreatedDate]}"')
    if 'record_cases_state' in paras_keys:
        if paras['record_cases_state'] == 0:
            where_list.append(f'{KEYWORD.Api.Task.RecordCasesUnSuccess} = 0')
        elif paras['record_cases_state'] == 1:
            where_list.append(f'{KEYWORD.Api.Task.RecordCasesUnSuccess} != 0')

    return splicing_sql_where_string(where_list)


def parse_case_search_criteria(paras: dict):
    """
    [ 解析任务搜索条件 ]
    
    """
    where_list = []
    paras_keys = paras.keys()
    if KEYWORD.Api.Case.Cid in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.Cid} = {paras[KEYWORD.Api.Case.Cid]}')
    if KEYWORD.Api.Case.Tid in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.Tid} = {paras[KEYWORD.Api.Case.Tid]}')
    if KEYWORD.Api.Case.Type in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.Type} = "{paras[KEYWORD.Api.Case.Type]}"')
    if KEYWORD.Api.Case.Name in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.Name} = "{paras[KEYWORD.Api.Case.Name]}"')
    if KEYWORD.Api.Case.State in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.State} = "{paras[KEYWORD.Api.Case.State]}"')
    if KEYWORD.Api.Case.CreatedDate in paras_keys:
        where_list.append(f'{KEYWORD.Api.Case.CreatedDate} = "{paras[KEYWORD.Api.Case.CreatedDate]}"')

    return splicing_sql_where_string(where_list)


def get_desc_limit(page: int = 1, number: int = 20) -> str:
    """
    [ 获取数据返回量区间限制 ]

    ---
    描述:
        默认是获取 1 页, 20 条数据。
    
    ---
    参数:
        page { int } : 页数。
        number { int } : 单页数据量。

    ---
    返回:
        Response : 拼接完成的 SQL LIMIT 语句参数。

    """
    if not isinstance(page, int):
        page = int(page)
    if not isinstance(number, int):
        number = int(number)
    
    # 计算偏移量
    limit_begin = 0
    if page > 1:
        limit_begin = (page - 1) * number

    return f'{ limit_begin }, { number }'


def splicing_sql_where_string(where_list: list) -> str:
    """
    [ 拼接 SQL 搜索条件 ]

    """
    where_key_str = ''
    number = 0
    end_number = len(where_list)
    if end_number >= 1:
        where_key_str += 'WHERE '
        for where in where_list:
            if number > 0:
                where_key_str += ' AND '
            where_key_str += where
            number += 1
    return where_key_str
