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
[ make测试接口 ]

"""
from flask import jsonify
from flask import Blueprint

from ...db import DB
from ...db import SQL
from ...api.server_request_handler import URL_PREFIX
from ...api.server_request_handler import ServerRequestHandler


BLUEPRINT_TEST = Blueprint('test', __name__)
""" [ 测试接口蓝图 ] """

BASE_USERS = {
    'admin': {
        'userId': 1, 
        'username': 'admin', 
        'realName': 'Rains Admin', 
        'avatar': 'http://mms0.baidu.com/it/u=2163504278, 3640533387&fm=253&app=138&f=JPEG&fmt=auto&q=75?w=500&h=707', 
        'desc': 'manager', 
        'password': 'admin', 
        'token': 'fakeToken1', 
        'homePath': '/dashboard/workbench', 
        'roles': [
            {
                'roleName': 'Super Admin', 
                'value': 'super'
            }, 
        ], 
    }
}
""" [ 临时用户数据 ] """


@BLUEPRINT_TEST.route(f'{URL_PREFIX}/login', methods=['POST'])
def get() -> jsonify:
    try:
        paras: dict = ServerRequestHandler.analysis_request_parameter(keys=['username', 'password'])

        if paras['username'] in BASE_USERS.keys():
            user = BASE_USERS[paras['username']]
            if user['password'] == paras['password']:
                result = {
                    'roles': user['roles'], 
                    'userId': user['userId'], 
                    'username': user['username'], 
                    'token': user['token'], 
                    'realName': user['realName'], 
                    'desc': user['desc'], 
                }
                return jsonify({
                    'code': 0, 
                    'result': result, 
                    'message': 'ok', 
                    'type': 'success'
                })
        else:
            return jsonify({
                'code': -1, 
                'result': None, 
                'message': 'Incorrect account or password！', 
                'type': 'error'
            })

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(f'{ error }')


@BLUEPRINT_TEST.route(f'{URL_PREFIX}/getUserInfo', methods=['GET'])
def get_user_info() -> jsonify:
    try:
        headers: dict = ServerRequestHandler.analysis_request_headers(keys=['Authorization'], must_keys=['Authorization'])
        token = headers['Authorization']

        if token:
            for _, v in BASE_USERS.items():
                if token == v['token']:
                    return jsonify({
                        'code': 0, 
                        'result': v, 
                        'message': 'ok', 
                        'type': 'success'
                    })
        else:
            return jsonify({
                'code': -1, 
                'result': None, 
                'message': 'Invalid token!', 
                'type': 'error'
            })

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(f'{ error }')


@BLUEPRINT_TEST.route(f'{URL_PREFIX}/logout', methods=['GET'])
def logout() -> jsonify:
    try:
        headers: dict = ServerRequestHandler.analysis_request_headers(keys=['Authorization'], must_keys=['Authorization'])
        token = headers['Authorization']

        if token:
            for k, v in BASE_USERS.items():
                if token == v['token']:
                    return jsonify({
                        'code': 0, 
                        'result': v, 
                        'message': 'Token has been destroyed', 
                        'type': 'success'
                    })
        else:
            return jsonify({
                'code': -1, 
                'result': None, 
                'message': 'Invalid token!', 
                'type': 'error'
            })

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(f'{ error }')


@BLUEPRINT_TEST.route(f'{URL_PREFIX}/table/getDemoList', methods=['GET'])
def table() -> jsonify:
    try:
        paras: dict = ServerRequestHandler.analysis_request_parameter(keys=['page', 'pageSize'])
        page = paras['page']
        page_size = paras['pageSize']

        headers: dict = ServerRequestHandler.analysis_request_headers(keys=['Authorization'], must_keys=['Authorization'])
        token = headers['Authorization']

        # 获取服务器数据
        db_r = DB.read(SQL.TASK.get_all_item(int(page), int(page_size)))
        task_all_count = DB.read(SQL.TASK.get_count_all())[0][0]
 
        r_task = []
        for t in db_r:
            task = {}
            task.update({'tid': t[0]})
            task.update({'name': t[1]})
            task.update({'remark': t[2]})
            task.update({'created_date': str(t[3])})
            task.update({'state': t[4]})
            task.update({'start_time': t[5]})
            task.update({'end_time': t[6]})
            task.update({'spend_time_s': t[7]})
            r_task.append(task)

        if token:
            for _, v in BASE_USERS.items():
                if token == v['token']:
                    return jsonify({
                        'code': 0, 
                        'result': {
                            'items': r_task, 
                            'total': task_all_count
                        }, 
                        'message': 'ok', 
                        'type': 'success'
                    })

    except BaseException as error:
        return ServerRequestHandler.unsuccessful(f'{ error }')
