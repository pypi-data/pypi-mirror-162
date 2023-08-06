# Copyright 2022. quinn.7@foxmail.com All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""
[ API 执行器 ]

"""
import re
import time

from .api_engine import ApiEngine
from ..common import _replace_variables_in_parameters
from ...base.log import LOG
from ...base.const import CONST
from ...base.language import LANGUAGE
from ...base.error import AwakenTaskRunningError
from ...base.error import AwakenTaskCaseAssertError
from ...server.task_db_broker import TaskDbBroker
from ...core.interpreter.grammar_parser import AwakenTask

class ApiRunner: ...


class ApiRunner:
    """
    [ API 执行器 ]

    """
    _task: AwakenTask
    _engine_action_map: dict
    _task_db_broker: TaskDbBroker


    def __init__(self, task: AwakenTask) -> None:
        self._task = task
        self._engine_action_map = {}
        self._task_db_broker = TaskDbBroker(CONST.TYPE.TYPE_API)

        # 解析获取驱动关键字对应的函数映射字典
        for n, v in ApiEngine.__dict__.items():
            if n[0] != '_':
                n = ''.join([n.title() for n in n.rsplit('_')])
                self._engine_action_map.update({ n : v })


    def start(self, api_engine: ApiEngine):
        """
        [ 开始任务 ]

        """
        task_state = CONST.TEXT.TEXT_END

        # 数据库创建任务
        self._task_db_broker.task_start(
            self._task.setting['TaskName'].value,
            self._task.setting['TaskDocs'].value
        )

        # 遍历任务的用例
        for case_object in self._task.test_cases:

            # 数据库创建用例
            case_id = self._task_db_broker.created_case(
                case_object.name,
                case_object.docs
            )

            try:
                state = CONST.TEXT.TEXT_END
                case_start_time = time.strftime("%H:%M:%S")
                case_start_timestamp = int(time.time())

                # 遍历用例的步骤
                for step in case_object.steps:
                    
                    # 替换步骤参数中的参数定义
                    step._parameters = _replace_variables_in_parameters(
                        self._task.namespace,
                        case_object.namespace,
                        step.parameters
                    )

                    try:
                        register = self._engine_action_map[step._function_name](api_engine, *step.parameters)
                    
                    except AwakenTaskCaseAssertError as error:
                        state = CONST.TEXT.TEXT_ERROR

                    except BaseException as error:
                        state = CONST.TEXT.TEXT_ERROR
                        error_message = LANGUAGE.ERROR.ERROR_MESSAGE_ENGINE_FUNCTION_RUNNING_ERROR.replace('FUNCTION_NAME', step._function_name).replace('ERROR', str(error))
                        raise AwakenTaskRunningError(error_message)

                    # 如果步骤对象存在赋值变量则赋值到对应的命名空间中
                    if step.assignment:
                        assignment_dollar_ident_count = step.assignment.count('$')
                        assignment_name = re.findall(r'\{(.*)\}', step.assignment)[0]
                        assignment_object = KeyValueObject()
                        assignment_object._number = 0
                        assignment_object._key = assignment_name
                        assignment_object._value = register

                        # 根据参数类型赋值到对应的命名空间中
                        if assignment_dollar_ident_count == 1:
                            case_object._namespace.update({assignment_object.key: assignment_object})
                        if assignment_dollar_ident_count == 2:
                            self._task._namespace.update({assignment_object.key: assignment_object})

            except BaseException as error:
                task_state = CONST.TEXT.TEXT_ERROR
                LOG.info(f'用例 [{ case_object.name }] 执行异常, 原因: { error }')
            
            finally:
                self._task_db_broker.update_case(
                    case_id,
                    state,
                    case_start_time,
                    case_start_timestamp,
                    ''  #执行步骤暂时省略
                )

        # 销毁
        self._task_db_broker.task_end(task_state)
