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
@ 模块     : 解释器结构体
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from .common import converting_para_format
from ...baseic.const import CONST
from ...baseic.error import AwakenConvertCodelinError
from ...kit.global_method import GlobalMethod


class AwakenTask: ...
class AwakenCase: ...
class AwakenCodeLine: ...


class AwakenTask:
    """
    [ Awaken任务对象 ]

    ---
    描述:
        该对象描述自动化任务的完整执行信息。

    """

    global_method: GlobalMethod = GlobalMethod()
    global_function_map: dict
    engine_function_map: dict
    namespace: dict
    test_cases: dict
    task_type: str
    basecodes: list


    def __init__(self, task_type: str, basecodes: list) -> None:
        """
        [ Awaken任务对象 :: 初始化 ]

        """
        self.task_type = task_type
        self.basecodes = basecodes


class AwakenCase:
    """
    [ Awaken用例 ]

    ---
    描述:
        该对象描述自动化任务用例的信息。

    """

    number: int
    name: str
    docs: str
    decorator: dict
    namespace: dict
    steps: list[AwakenCodeLine]


    def __init__(self, number, name, docs='', *_) -> None:
        self.number = number
        self.name = name
        self.docs = docs
        self.decorator = {}
        self.namespace = {}
        self.steps = []


class AwakenCodeLine:
    """
    [ 代码行对象 ]

    ---
    描述:
        该对象描述自动化任务用例的信息。

    """

    number: int
    region: str
    type: str
    give_region: str
    give_name: str
    give_value: str
    funtion_region: str
    funtion_name: str
    funtion_value: str
    case_name: str
    case_docs: str
    decorator_key: str
    decorator_value: str
    assert_value: str


    def __init__(self, codeline: str) -> None:
        codeline_splint = codeline.split(' ')
        self.number = codeline_splint[0]
        self.region = codeline_splint[1]
        self.type = codeline_splint[2]

        if self.type == CONST.Interpreter.CodeLineType.Give:
            _give_splint = codeline_splint[3].split(CONST.Interpreter.GrammarSymbol.ScopePrefix)
            self.give_region = _give_splint[0]
            self.give_name = _give_splint[1]
            self.give_value = converting_para_format(codeline_splint[4])

        elif self.type == CONST.Interpreter.CodeLineType.RGive:
            _give_splint = codeline_splint[3].split(CONST.Interpreter.GrammarSymbol.ScopePrefix)
            _run_splint = codeline_splint[4].split(CONST.Interpreter.GrammarSymbol.ScopePrefix)
            self.give_region = _give_splint[0]
            self.give_name = _give_splint[1]
            self.funtion_region = _run_splint[0]
            self.funtion_name = _run_splint[1]
            self.funtion_value = []
            if len(codeline_splint) >= 6:
                for value in codeline_splint[5:]:
                    self.funtion_value.append(converting_para_format(value))

        elif self.type == CONST.Interpreter.CodeLineType.Run:
            _run_splint = codeline_splint[3].split(CONST.Interpreter.GrammarSymbol.ScopePrefix)
            self.funtion_region = _run_splint[0]
            self.funtion_name = _run_splint[1]
            self.funtion_value = []
            if len(codeline_splint) >= 5:
                for value in codeline_splint[4:]:
                    self.funtion_value.append(converting_para_format(value))

        elif self.type == CONST.Interpreter.CodeLineType.SCase:
            self.case_name = codeline_splint[3]
            self.case_docs = codeline_splint[4] if len(codeline_splint) == 5 else ''

        elif self.type == CONST.Interpreter.CodeLineType.SDecorator:
            self.decorator_key = codeline_splint[2]
            self.decorator_value = codeline_splint[3]

        elif self.type == CONST.Interpreter.CodeLineType.Assert:
            self.assert_value = codeline_splint[3:]

        else:
            raise AwakenConvertCodelinError(CONST.Error.Interpreter.GrammarBaseCodeLineTypeError.replace('#TYPE#', self.type))
