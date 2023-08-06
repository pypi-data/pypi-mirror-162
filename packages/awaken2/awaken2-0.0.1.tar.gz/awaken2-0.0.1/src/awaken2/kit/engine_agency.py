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
@ 模块     : 引擎代理
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from .web.web_runner import WebRunner
from ..baseic.const import CONST
from ..core.interpreter.structural import AwakenTask
from ..core.interpreter.task_preprocessor import TaskPreprocessor


class EngineAgency: ...


class EngineAgency:
    """
    [ 引擎代理 ]

    ---
    描述:
        NULL

    """
    
    task_preprocessor: TaskPreprocessor
    """ 任务预处理程序 """


    def __init__(self) -> None:
        self.task_preprocessor = TaskPreprocessor()


    def start(self, task: AwakenTask):

        task = self.task_preprocessor.pretreatment(task)

        if task.task_type == CONST.Type.Task.Web:
            engine = ''
            runner = WebRunner(task)
            runner.start(engine)

        # if task.task_type == CONST.Type.Task.Api:
        #     engine = ApiEngine()
        #     runner = ApiRunner(task)
        #     runner.start(engine)
