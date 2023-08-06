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
@ 模块     : 类型常量
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""


class Task: ...
class Browser: ...


class Task:
    """
    [ 类型常量索引 :: 任务 ]

    ---
    描述: 
        NULL
        
    """

    Web = 'WEB'
    """ WEB """

    Api = 'API'
    """ API """


class Browser:
    """
    [ 类型常量索引 :: 浏览器 ]

    ---
    描述: 
        NULL
        
    """

    Webkit = 'Webkit'
    """ WebKit浏览器 """

    Firefox = 'Firefox'
    """ 火狐浏览器 """

    Chromium = 'Chromium'
    """ 谷歌浏览器 """
