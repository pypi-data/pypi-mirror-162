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
@ 模块     : 脚本字段关键字
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL
    
"""


class Namespace: ...
class Decorator: ...


class Namespace:
    """
    [ 脚本字段关键字索引 :: 命名空间 ]

    ---
    描述: 
        脚本的命名空间相关的字段。

    """

    TaskType = 'TaskType'
    """ 任务类型 """

    TaskName = 'TaskName'
    """ 任务名称 """

    TaskDocs = 'TaskDocs'
    """ 任务注释 """


class Decorator:
    """
    [ 脚本字段关键字索引 :: 装饰器 ]

    ---
    描述: 
        脚本的装饰器相关的字段。

    """

    BrowserType = 'BrowserType'
    """ 浏览器类型 """
