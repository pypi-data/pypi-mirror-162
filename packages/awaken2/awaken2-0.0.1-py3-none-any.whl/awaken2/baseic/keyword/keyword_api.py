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
@ 模块     : API字段关键字
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""


class Task: ...
class Case: ...


class Task:
    """
    [ API字段关键字索引 :: 任务 ]

    ---
    描述: 
        任务相关的字段。

    """

    Tid = 'tid'
    """ 编号 """

    Name = 'name'
    """ 名称 """

    Type = 'type'
    """ 类型 """

    Remark = 'remark'
    """ 备注 """

    CreatedDate = 'created_date'
    """ 创建日期 """

    State = 'state'
    """ 状态 """

    StartTime = 'start_time'
    """ 开始时间 """

    EndTime = 'end_time'
    """ 结束时间 """

    SpendTime = 'spend_time'
    """ 消耗时间 """

    RecordCasesAll = 'record_cases_all'
    """ 统计所有用例数 """

    RecordCasesSuccess = 'record_cases_success'
    """ 统计成功用例数 """

    RecordCasesUnSuccess = 'record_cases_unsuccess'
    """ 统计失败用例数 """


class Case:
    """
    [ API字段关键字索引 :: 用例 ]

    ---
    描述: 
        用例相关的字段。
        
    """

    Cid = 'cid'
    """ 用例编号 """

    Tid = Task.Tid
    """ 所属任务编号 """

    Name = Task.Name
    """ 名称 """

    Type = Task.Type
    """ 类型 """

    Remark = Task.Remark
    """ 备注 """

    CreatedDate = Task.CreatedDate
    """ 创建日期 """

    State = Task.State
    """ 状态 """

    StartTime = Task.StartTime
    """ 开始时间 """

    EndTime = Task.EndTime
    """ 结束时间 """

    SpendTime = Task.SpendTime
    """ 消耗时间 """

    RunStep = 'run_step'
    """ 执行步骤 """
