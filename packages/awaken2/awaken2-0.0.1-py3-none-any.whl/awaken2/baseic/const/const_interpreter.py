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
@ 模块     : 解释器常量
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""


class StatementIdent: ...
class GrammarSymbol: ...
class CodeLineType: ...
class CodeLineScopet: ...


KEYWORD_BASECODE_FILE_SUFFIX = 'basecode'
"""
[ 关键字 :: 编码文件后缀 ]
描述: 底层编码文件的命名拼接字段。
"""

KEYWORD_IDENT_SCOPE_UNIVERSE = 'UNIVERSE'
""" 
[ 关键字 :: 公共作用域标识  ]
描述: 底层编码行的作用域标识, 表示作用于全域。
"""

SYMBOL_BASECODE_FILE_SEPARATOR = '-'
""" 
[ 符号 :: 编码文件间隔符  ]
描述: 底层编码文件的命名拼接间隔符号。
"""


class StatementIdent:
    """
    [ 解释器常量索引 :: 声明标识 ]

    ---
    描述: 
        底层编码行的声明事件参数标识。

    """

    Case = 'CASE'
    """ 声明用例标识 """

    Deco = 'DECO'
    """ 声明装饰器标识 """


class GrammarSymbol:
    """
    [ 解释器常量索引 :: 语法符号 ]

    ---
    描述: 
        Awaken脚本语法中的语法符号。

    """

    Annotation = '##'
    """ 注释符 """

    Give = '='
    """ 赋值符 """

    Statement = '::'
    """ 声明符 """

    Run = '>>'
    """ 执行符 """

    Assert = '??'
    """ 断言符 """

    Call = '@'
    """ 方法调用符 """

    Quote = '$'
    """ 资源引用符 """

    VariablePath = '::'
    """ 字典路径应用符 """

    ScopePrefix = '?>'
    """ 作用域前缀 """


class CodeLineType:
    """
    [ 解释器常量索引 :: 编码行类型 ]

    ---
    描述: 
        NULL

    """

    Give = 'GIVE'
    """ 赋值类型 """

    RGive = 'RGIVE'
    """ 执行赋值类型 """

    SCase = 'SCASE'
    """ 声明用例类型 """

    SDecorator = 'SDECORATOR'
    """ 声明装饰器类型 """

    Run = 'RUN'
    """ 执行类型 """

    Assert = 'ASSERT'
    """ 断言类型 """


class CodeLineScopet:
    """
    [ 解释器常量索引 :: 编码行作用域 ]

    ---
    描述:
        NULL

    """

    Global = 'GLOBAL'
    """ 全局 """

    Local = 'LOCAL'
    """ 局部 """
