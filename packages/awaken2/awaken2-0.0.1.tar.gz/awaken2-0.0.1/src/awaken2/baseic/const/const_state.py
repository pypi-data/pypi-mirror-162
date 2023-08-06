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
@ 模块     : 状态常量
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""


class Result: ...
class Switch: ...
class RunProcess: ...


class Result:
    """
    [ 状态常量索引 :: 结果 ]

    ---
    描述: 
        NULL

    """

    Null = 'Null'
    """ NULL """

    Success = '成功'
    """ 成功 """

    Unsuccess = '失败'
    """ 失败 """

    Error = '异常'
    """ 异常 """


class Switch:
    """
    [ 状态常量索引 :: 开关 ]

    ---
    描述: 
        NULL

    """

    On = '开'
    """ 开 """

    Off = '关'
    """ 关 """


class RunProcess:
    """
    [ 状态常量索引 :: 运行过程 ]

    ---
    描述: 
        NULL
        
    """
    
    Start = '开始'
    """ 开始 """

    End = '结束'
    """ 结束 """

    Suspend = '暂停'
    """ 暂停 """
