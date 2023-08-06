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
@ 模块     : Awaken任务预处理程序
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from .structural import AwakenTask
from .structural import AwakenCase
from .structural import AwakenCodeLine
from ...baseic.log import LOG
from ...baseic.const import CONST
from ...baseic.keyword import KEYWORD
from ...baseic.error import AwakenTaskPretreatmentError
from ...kit.common import MAPPING_TASK_TYPE_TO_ENGINE


class TaskPreprocessor:
    """
    [ Awaken任务预处理程序 ]

    ---
    描述:
        NULL

    """
    
    _task: AwakenTask
    """ 任务对象 """

    def pretreatment(self, task: AwakenTask):
        self._task = task
        self._init_namespace_by_task_type()
        self._running_preprocessing_instruction()
        return self._task


    def _init_namespace_by_task_type(self):
        self._task.namespace: dict = {
            KEYWORD.Script.Namespace.TaskType: None,
            KEYWORD.Script.Namespace.TaskName: None,
            KEYWORD.Script.Namespace.TaskDocs: None
        }

        self._task.test_cases: dict = {}

        if self._task.task_type == CONST.Type.Task.Web:
            self._task.namespace[KEYWORD.Script.Namespace.TaskType] = CONST.Type.Task.Web
            self._task.namespace[KEYWORD.Script.Decorator.BrowserType] = CONST.Type.Browser.Chromium

        elif self._task.task_type == CONST.Type.Task.Api:
            self._task.namespace[KEYWORD.Script.Namespace.TaskType] = CONST.Type.Task.Api


    def _running_preprocessing_instruction(self):
        """
        [ 运行预处理指令 ]

        ---
        描述:
            NULL

        """

        # --------------------------------------------------------------------
        # 解析全局&&引擎方法映射字典
        # --------------------------------------------------------------------
        self._task.global_function_map = {}
        for fn, fv in type(self._task.global_method).__dict__.items():
            if fn[0] != '_':
                fn = ''.join([n.title() for n in fn.rsplit('_')])
                self._task.global_function_map.update({ fn : fv })

        self._task.engine_function_map = {}
        engine_type = MAPPING_TASK_TYPE_TO_ENGINE[self._task.task_type]
        for fn, fv in engine_type.__dict__.items():
            if fn[0] != '_':
                fn = ''.join([n.title() for n in fn.rsplit('_')])
                self._task.engine_function_map.update({ fn : fv })

        # --------------------------------------------------------------------
        # 循环全局域语句
        # 用例域语句将被存放至 test_cases 字典中等待引擎解析
        # --------------------------------------------------------------------
        for codeline in self._task.basecodes:
            awaken_codeline = AwakenCodeLine(codeline)

            # 公域语句
            if awaken_codeline.region == CONST.Interpreter.KEYWORD_IDENT_SCOPE_UNIVERSE:
                
                # 赋值逻辑
                if awaken_codeline.type == CONST.Interpreter.CodeLineType.Give:
                    self._give_global_assignment(awaken_codeline.give_name, awaken_codeline.give_value)

                # 执行并赋值逻辑
                elif awaken_codeline.type == CONST.Interpreter.CodeLineType.RGive:
                    result = self._running_common_function(awaken_codeline.funtion_name, awaken_codeline.funtion_value)
                    self._give_global_assignment(awaken_codeline.give_name, result)

                # 执行逻辑
                elif awaken_codeline.type == CONST.Interpreter.CodeLineType.Run:
                    self._running_common_function(awaken_codeline.funtion_name, awaken_codeline.funtion_value)

                # 声明逻辑
                elif awaken_codeline.type == CONST.Interpreter.CodeLineType.SCase:
                    awaken_case = AwakenCase(
                        awaken_codeline.number,
                        awaken_codeline.case_name,
                        awaken_codeline.case_docs,
                    )
                    self._task.test_cases[awaken_case.name] = awaken_case

            # 私域语句
            else:

                # 装饰器逻辑
                if awaken_codeline.type == CONST.Interpreter.CodeLineType.SDecorator:
                    self._task.test_cases[awaken_codeline.region].decorator.update({awaken_codeline.decorator_key : awaken_codeline.decorator_value})

                # 执行并赋值逻辑
                elif awaken_codeline.type == CONST.Interpreter.CodeLineType.RGive:
                    self.verify_validity_method(awaken_codeline)

                # 执行逻辑
                elif awaken_codeline.type == CONST.Interpreter.CodeLineType.Run:
                    self.verify_validity_method(awaken_codeline)

                # 其他语句
                else:
                    self._task.test_cases[awaken_codeline.region].steps.append(awaken_codeline)


    def _give_global_assignment(self, give_name: str, give_value: str):
        """
        [ 公域赋值封装 ]

        ---
        描述:
            NULL
        
        """
        give_path_node = give_name.split(CONST.Interpreter.GrammarSymbol.VariablePath)
        give_path_node_number = len(give_path_node)
        current_node = self._task.namespace
        i = 1
        if give_path_node_number > 1:
            for node in give_path_node:
                if i == give_path_node_number:
                    current_node.update({node: give_value})
                else:
                    if node not in current_node.keys():
                        current_node.update({node: {}})
                    current_node = current_node[node]
                    i += 1
        else:
            self._task.namespace.update({give_name : give_value})


    def _running_common_function(self, name: str, paras: list):
        """
        [ 公域运行方法封装 ]

        ---
        描述:
            NULL
        
        """
        try:
            if name not in self._task.global_function_map.keys():
                raise AwakenTaskPretreatmentError(CONST.Error.Interpreter.GrammarGlobalMethodWrongful('#NAME#', name))

            new_function_value = []
            if len(paras) > 0:
                for value in paras:
                    if isinstance(paras, str):
                        value_symbol_count = value[0:2].count(CONST.Interpreter.GrammarSymbol.Call)
                        key = value[value_symbol_count:]

                        if value_symbol_count == 2:
                            function_value_split = key.split(CONST.Interpreter.GrammarSymbol.Statement)
                            current_node = self._task.namespace

                            if len(function_value_split) > 1:
                                for node in function_value_split:
                                    try:
                                        current_node = current_node[node]
                                    except KeyError:
                                        AwakenTaskPretreatmentError(CONST.Error.Interpreter.GrammarNamespaceNodeNotExist('#NODE#', node))
                            else:
                                try:
                                    current_node = current_node[function_value_split[0]]
                                except:
                                    AwakenTaskPretreatmentError(CONST.Error.Interpreter.GrammarNamespaceNodeNotExist('#NODE#', node))
                        
                            new_function_value.append(current_node)
                    
                    else:
                        new_function_value.append(value)

            result = self._task.global_function_map[name](self._task.global_method, *new_function_value)
            return result

        except KeyError:
            raise AwakenTaskPretreatmentError(CONST.Error.Interpreter.GrammarGlobalMethodWrongful('#NAME#', name))


    def verify_validity_method(self, awaken_codeline):
        """
        [ 校验方法的有效性 ]

        ---
        描述:
            NULL

        """
        function_map = None
        if awaken_codeline.funtion_region == CONST.Interpreter.CodeLineScopet.Global:
            function_map = self._task.global_function_map.keys()
        else:
            function_map = self._task.engine_function_map.keys()

        if awaken_codeline.funtion_name in function_map:
            self._task.test_cases[awaken_codeline.region].steps.append(awaken_codeline)
        else:
            raise AwakenTaskPretreatmentError(CONST.Error.Interpreter.GrammarGlobalMethodWrongful('#NAME#', awaken_codeline.funtion_name))
            