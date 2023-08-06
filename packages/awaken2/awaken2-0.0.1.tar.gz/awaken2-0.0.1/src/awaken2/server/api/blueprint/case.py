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
[ 用例接口 ]

"""
import math

from flask import Response
from flask import Blueprint

from ...db import DB
from ...db import SQL
from ...api.server_request_handler import URL_PREFIX
from ...api.server_request_handler import ServerRequestHandler
from ....baseic.keyword import KEYWORD


case_blueprint = Blueprint('case', __name__)
""" 用例接口蓝图实例 """


@case_blueprint.route(''.join([URL_PREFIX, '/case/case_count']), methods=['GET'])
def case_count() -> Response:
    """
    [ 获取用例数量 ]

    ---
    可选参数:
        tid           { int } : 任务编号
        type          { str } : 类型
        state         { str } : 状态
        created_date  { str } : 创建日期, 例如 2022-02-02

    """
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['tid', 'type', 'state', 'created_date']
        )

        # 处理任务列表数据
        case_count = DB.read(SQL.Case.get_count(paras))[0][0]

        result = {
            'case_count': case_count
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@case_blueprint.route(''.join([URL_PREFIX, '/case/case_list']), methods=['GET'])
def case_list() -> Response:
    """
    [ 获取用例列表 ]

    ---
    必传参数:
        page                { int } : 页数
        number              { int } : 单页数据量

    ---
    可选参数:
        tid           { int } : 所属任务编号
        cid           { int } : 用例编号
        type          { str } : 类型
        state         { str } : 状态
        created_date  { str } : 创建日期, 例如 2022-02-02

    """
    try:
        # 解析请求参数
        paras: dict = ServerRequestHandler.analysis_request_parameter(
            keys=['tid', 'cid', 'type', 'state', 'created_date', 'page', 'number'],
            must_keys=['page', 'number']
        )

        # 从数据库中获取原始数据
        base_case_list = DB.read(SQL.Case.get_case_list(paras))

        # 处理任务列表数据
        case_list = []
        for item in base_case_list:
            case_info = {}
            case_info.update({KEYWORD.Api.Case.Cid: item[0]})
            case_info.update({KEYWORD.Api.Case.Tid: item[1]})
            case_info.update({KEYWORD.Api.Case.Name: item[2]})
            case_info.update({KEYWORD.Api.Case.Type: item[3]})
            case_info.update({KEYWORD.Api.Case.Remark: item[4]})
            case_info.update({KEYWORD.Api.Case.State: item[5]})
            case_info.update({KEYWORD.Api.Case.CreatedDate: item[6]})
            case_info.update({KEYWORD.Api.Case.StartTime: item[7]})
            case_info.update({KEYWORD.Api.Case.EndTime: item[8]})
            case_info.update({KEYWORD.Api.Case.SpendTime: item[9]})
            case_info.update({KEYWORD.Api.Case.RunStep: item[10]})
            case_list.append(case_info)

        # 处理分页相关数据
        task_count = len(base_case_list)
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
            'tasks': case_list
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))


@case_blueprint.route(''.join([URL_PREFIX, '/case/case_delete']), methods=['POST'])
def case_delete() -> Response:
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
    try:
        # 解析请求参数
        paras = ServerRequestHandler.analysis_request_parameter(
            keys=['tid', 'cid', 'type', 'state', 'created_date']
        )

        # 从数据库中获取原始数据
        base_case_id_list = DB.lock_read(SQL.Case.get_id_list(paras))

        case_id_list = []
        case_id_count = 0
        del_message = '删除失败, 无法查询到用例 !'
        if len(base_case_id_list) > 0:
            for i in base_case_id_list:
                case_id_list.append(i[0])
            case_id_count = len(case_id_list)

            for cid in case_id_list:
                DB.lock_write(SQL.Case.delete({KEYWORD.Api.Case.Cid : cid}))
                DB.commit()
                del_message = f'成功删除 [{case_id_count}] 条数据 !'

        result = {
            'del_message': del_message,
            'del_count': case_id_count
        }

        return ServerRequestHandler.successful(result)

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(str(error))
