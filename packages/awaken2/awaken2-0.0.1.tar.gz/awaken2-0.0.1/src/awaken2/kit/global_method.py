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
@ 模块     : 脚本全局方法
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import yaml
import time
from pathlib import Path

from ..baseic.log import LOG
from ..baseic.const import CONST
from ..baseic.decorator import singleton_pattern


class GlobalMethod: ...


@singleton_pattern
class GlobalMethod:
    """
    [ 脚本全局方法 ]
    
    """


    def sleep(self, wait: int):
        """
        [ 等待 ]

        ---
        描述:
            NULL

        """
        time.sleep(wait)


    def logout(self, message: str, level=CONST.Common.LogLevel.Info) -> str:
        """
        [ 日志输出 ]

        ---
        描述:
            输出日志到控制台。
        
        ---
        参数:
            message { str } : 输出的日志信息。
            level   { str } : 日志等级。
        
        """
        LOG.out_map(level, message)
        return message


    def read_yaml(self, yaml_path_str: str):
        """
        [ 读取 YAML 文件 ]

        ---
        描述:
            NULL

        """
        yaml_path_str = Path(yaml_path_str)
        with open(file=yaml_path_str, mode='r', encoding='UTF-8') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data


    def get_type(self, data):
        if isinstance(data, str):
            return 'str'
        elif isinstance(data, dict):
            return 'dict'
        elif isinstance(data, int):
            return 'int'
        elif isinstance(data, float):
            return 'float'
        else:
            return 'None'
