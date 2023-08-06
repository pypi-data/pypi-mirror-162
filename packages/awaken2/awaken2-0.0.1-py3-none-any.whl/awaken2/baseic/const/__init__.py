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
@ 模块     : 常量索引
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
from . import const_api
from . import const_common
from . import const_error
from . import const_interpreter
from . import const_path
from . import const_state
from . import const_type


class AwakenConst: ...


class AwakenConst:
    """
    [ 常量索引 ]

    ---
    描述:
        NULL

    """


    @property
    def Api(self) -> const_api:
        """
        [ 接口常量 ]

        ---
        描述: 
            NULL

        """
        return const_api


    @property
    def Common(self) -> const_common:
        """
        [ 通用常量 ]

        ---
        描述: 
            NULL

        """
        return const_common


    @property
    def Error(self) -> const_error:
        """
        [ 错误常量 ]

        ---
        描述: 
            NULL

        """
        return const_error


    @property
    def Interpreter(self) -> const_interpreter:
        """
        [ 解释器常量 ]

        ---
        描述: 
            NULL

        """
        return const_interpreter


    @property
    def State(self) -> const_state:
        """
        [ 状态常量 ]

        ---
        描述: 
            NULL

        """
        return const_state


    @property
    def Path(self) -> const_path:
        """
        [ 路径常量 ]

        ---
        描述: 
            NULL

        """
        return const_path


    @property
    def Type(self) -> const_type:
        """
        [ 类型常量 ]

        ---
        描述: 
            NULL

        """
        return const_type


CONST: AwakenConst = AwakenConst()
""" 常量索引实例 """
