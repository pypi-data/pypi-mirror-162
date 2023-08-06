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
[ 任务接口 ]

"""
import math

from flask import Response
from flask import Blueprint

from ...db import DB
from ...db import SQL
from ...api.server_request_handler import URL_PREFIX
from ...api.server_request_handler import ServerRequestHandler
from ....baseic.keyword import KEYWORD


task_blueprint = Blueprint('task', __name__)
""" 任务接口蓝图实例 """


@task_blueprint.route(''.join([URL_PREFIX, '/task/task_count']), methods=['GET'])
def task_count() -> Response:
    """
    [ 获取任务数量 ]

    ---
    可选参数:
        type                { str } : 类型
        state               { str } : 状态
        created_date        { str } : 创建日期, 例如 2022-02-02
        record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

    """
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['type', 'state', 'created_date', 'record_cases_state']
        )

        # 处理任务列表数据
        task_count = DB.read(SQL.Task.get_count(paras))[0][0]

        result = {
            'task_count': task_count
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@task_blueprint.route(''.join([URL_PREFIX, '/task/task_exist_task_date_list']), methods=['GET'])
def task_exist_dates() -> Response:
    """
    [ 获取去重后的所有存在任务的日期列表 ]

    ---
    可选参数:
        type                { str } : 类型
        state               { str } : 状态
        created_date        { str } : 创建日期, 例如 2022-02-02
        record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

    """
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['type', 'state', 'created_date', 'record_cases_state']
        )

        # 处理任务列表数据
        base_exist_task_dates = DB.read(SQL.Task.get_exist_task_dates(paras))
        exist_task_dates = []
        if len(base_exist_task_dates) > 0:
            for date in base_exist_task_dates:
                exist_task_dates.append(date[0])

        result = {
            'exist_task_dates': exist_task_dates
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@task_blueprint.route(''.join([URL_PREFIX, '/task/task_spend_time']), methods=['GET'])
def task_spend_time() -> Response:
    """
    [ 获取查询任务的消耗时间 ]

    ---
    可选参数:
        tid                 { int } : 任务编号
        type                { str } : 类型
        state               { str } : 状态
        created_date        { str } : 创建日期, 例如 2022-02-02
        record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

    """
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['tid','type', 'state', 'created_date', 'record_cases_state']
        )

        # 处理任务列表数据
        base_task_spend_time = DB.read(SQL.Task.get_spend_time(paras))[0][0]
        task_spend_time = 0
        if base_task_spend_time:
            task_spend_time = base_task_spend_time

        result = {
            'task_spend_time': task_spend_time
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@task_blueprint.route(''.join([URL_PREFIX, '/task/task_list']), methods=['GET'])
def task_list() -> Response:
    """
    [ 获取任务列表 ]

    ---
    必传参数:
        page                { int } : 页数
        number              { int } : 单页数据量

    ---
    可选参数:
        tid                 { int } : 任务编号
        type                { str } : 类型
        state               { str } : 状态
        created_date        { str } : 创建日期, 例如 2022-02-02
        record_cases_state  { int } : 统计用例状态, 0表示全部成功, 1表示存在失败, 2表示存在异常

    """
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['tid', 'type', 'state', 'created_date', 'record_cases_state', 'page', 'number'],
            must_keys=['page', 'number']
        )

        # 从数据库中获取原始数据
        base_task_list = DB.read(SQL.Task.get_task_list(paras))

        # 处理任务列表数据
        task_list = []
        for item in base_task_list:
            task_info = {}
            task_info.update({KEYWORD.Api.Task.Tid: item[0]})
            task_info.update({KEYWORD.Api.Task.Type: item[1]})
            task_info.update({KEYWORD.Api.Task.Name: item[2]})
            task_info.update({KEYWORD.Api.Task.Remark: item[3]})
            task_info.update({KEYWORD.Api.Task.State: item[4]})
            task_info.update({KEYWORD.Api.Task.CreatedDate: item[5]})
            task_info.update({KEYWORD.Api.Task.StartTime: item[6]})
            task_info.update({KEYWORD.Api.Task.EndTime: item[7]})
            task_info.update({KEYWORD.Api.Task.SpendTime: item[8]})
            task_info.update({KEYWORD.Api.Task.RecordCasesAll: item[9]})
            task_info.update({KEYWORD.Api.Task.RecordCasesSuccess: item[10]})
            task_info.update({KEYWORD.Api.Task.RecordCasesUnSuccess: item[11]})
            task_list.append(task_info)

        # 处理分页相关数据
        task_count = len(base_task_list)
        paging = {}
        page = paras['page']
        number = paras['number']
        max_page = math.ceil(task_count / number)
        paging.update({'current_page': page})
        paging.update({'current_count': number})
        paging.update({'max_page': max_page})
        paging.update({'max_count': task_count})
        paging.update({'next_page': page + 1 if page < max_page else page})
        paging.update({'back_page': page - 1 if page > 1 else 1})

        result = {
            'paging': paging,
            'tasks': task_list
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@task_blueprint.route(''.join([URL_PREFIX, '/task/task_delete']), methods=['POST'])
def task_delete() -> Response:
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
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['tid', 'type', 'state', 'created_date', 'record_cases_state']
        )

        # 从数据库中获取原始数据
        base_task_id_list = DB.lock_read(SQL.Task.get_id_list(paras))

        task_id_list = []
        task_id_count = 0
        del_message = '删除失败, 无法查询到任务 !'
        if len(base_task_id_list) > 0:
            for i in base_task_id_list:
                task_id_list.append(i[0])
            task_id_count = len(task_id_list)

            for tid in task_id_list:
                DB.lock_write(SQL.Task.delete({KEYWORD.Api.Task.Tid : tid}))
                DB.lock_write(SQL.Case.delete({KEYWORD.Api.Task.Tid : tid}))
                DB.commit()
                del_message = f'成功删除 [{task_id_count}] 条数据 !'

        result = {
            'del_message': del_message,
            'del_count': task_id_count
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))
