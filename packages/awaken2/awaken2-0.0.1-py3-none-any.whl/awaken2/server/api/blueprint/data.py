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
[ 数据接口 ]

"""
from flask import Response
from flask import Blueprint

from ...db import DB
from ...db import SQL
from ...api.server_request_handler import URL_PREFIX
from ...api.server_request_handler import ServerRequestHandler


data_blueprint = Blueprint('data', __name__)
""" 数据接口蓝图实例 """


@data_blueprint.route(''.join([URL_PREFIX, '/data/summarize']), methods=['GET'])
def summarize() -> Response:
    """
    [ 获取执行信息概述 ]

    """
    try:
        # 获取最新执行数据
        new_exec_data = {}
        # 获取日期
        date = DB.read(SQL.TASK.get_date_list())[0][0]
        new_exec_data.update({'date': date})
        # 获取任务数量
        new_exec_data.update({'task_count': DB.read(SQL.TASK.get_count_from_date(date)[0][0])})
        # 获取用例数量
        new_exec_data.update({'case_count': DB.read(SQL.CASE.get_count_from_date(date))[0][0]})
        # 获取异常用例数量
        new_exec_data.update({'fail_case_count': DB.read(SQL.CASE.get_count_fail_from_data(date))[0][0]})
        # 获取消耗时间
        new_exec_data.update({'spend_time': round((DB.read(SQL.TASK.get_spend_time_from_data(date))[0][0] / 60), 2)})

        # 获取历史执行数据
        history_exec_data = {}
        # 获取任务数量
        history_exec_data.update({'task_count': DB.read(SQL.TASK.get_count_all())[0][0]})
        # 获取用例数量
        history_exec_data.update({'case_count': DB.read(SQL.CASE.get_count_all())[0][0]})
        # 获取异常用例数量
        history_exec_data.update({'fail_case_count': DB.read(SQL.CASE.get_count_fail())[0][0]})
        # 获取消耗时间
        history_exec_data.update({'spend_time': round((DB.read(SQL.TASK.get_spend_time_all())[0][0] / 60), 2)})
        # 获取异常任务数量
        history_exec_data.update({'fail_task_count': DB.read(SQL.TASK.get_count_fail())[0][0]})

        return ServerRequestHandler.successful({
            'new_exec': new_exec_data, 
            'history_exec': history_exec_data
        })

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(error)
