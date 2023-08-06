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
@ 模块     : 错误常量
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""


class Interpreter: ...
class PerformPool: ...


AWAKEN_LOG_OUTPUT_ERROR = '日志等级不存在 :: [ #LEVEL# ] !'


class Interpreter:
    """
    [ 错误常量 :: 解释器 ]

    ---
    描述: 
        NULL
        
    """

    GrammarSymbolWrongful = '语法符号不合法 :: [ #SYMBOL# ] !'
    """ 语法符号不合法 """

    GrammarMethodNotCallSymbol = '请使用 "#CALL##CALL#" 调用全局方法, 在用例空间中使用 "#CALL#" 调用引擎方法 !'
    """ 语法方法未使用调用符号 """

    GrammarGlobalProhibitUsingLocalMethod = '全域命名空间中无法调用引擎方法, 请使用 "#CALL##CALL#" 调用全局方法 !'
    """ 语法全局禁止使用本地方法 """

    GrammarStatementWrongful = '声明关键字 [ #KEYWORD# ] 不是合法的关键字 !'
    """ 语法声明关键字不合法 """

    GrammarStatementNoParameters = '声明关键字 [ #KEYWORD# ] 没有携带参数 !'
    """ 语法声明关键字无参数 """

    GrammarUseCaseNoAssertion = '用例 [ #CASE_NAME# ] 没有断言语句 !'
    """ 语法用例未断言 """

    GrammarBaseCodeLineTypeError = '无法识别的编码行类型 :: [ #TYPE# ] !'
    """ 语法底层编码行类型异常 """

    GrammarGlobalMethodWrongful = '不合法的全局方法 :: [ #NAME# ] !'
    """ 语法全局方法不合法 """

    GrammarNamespaceNodeNotExist = '命名空间不存在节点 [ #NODE# ]'
    """ 语法命名空间不存在节点 """


class PerformPool:
    """
    [ 错误常量 :: 执行器 ]

    ---
    描述: 
        NULL
        
    """

    TaskQueueConsumedMessage = '任务队列消耗完毕, 正在等待任务执行 !'

    TaskRunningConsumedMessage = '任务全部执行完毕, 退出程序 !'

    ServerRunningMessage = '执行服务运行中 >> 端口号 :: [ #PORT# ] !'

    ListeningProcessStarted = '监听进程已启动 ...'
