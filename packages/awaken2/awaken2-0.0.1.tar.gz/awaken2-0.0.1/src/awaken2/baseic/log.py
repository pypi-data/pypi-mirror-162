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
@ 模块     : Awaken日志
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import time
import logging

from .const import CONST
from .config import CONFIG
from .decorator import singleton_pattern
from .error import AwakenLogCreationError
from .error import AwakenLogOutputError


class AwakenLog: ...


_LEVEL_FILE_HANDLES = [
    CONST.Common.LogLevel.Debug,
    CONST.Common.LogLevel.Info,
    CONST.Common.LogLevel.Error,
    CONST.Common.LogLevel.Warning,
    CONST.Common.LogLevel.Critical,
]
""" 文件流处理器的日志级别 """

_LOG_OUTPUT_STRUCTURE = logging.Formatter('[%(asctime)s] [%(levelname)7s] %(message)s')
""" 日志输出格式对象 """


@singleton_pattern
class AwakenLog:
    """ 
    [ 日志模块 ]

    ---
    描述:
        NULL
    
    """

    _logger: logging.Logger = logging.getLogger()
    """ 日志记录器 """


    def __init__(self) -> None:
        """ 
        [ 日志模块 :: 实例化 ]
        
        ---
        异常:
            AwakenLogCreationError : 创建日志实例异常。
        
        """
        try:
            # 从配置文件中获取日志等级
            self._logger.setLevel(CONFIG.log_level_floor.upper())
            self._logger.handlers.clear()

            # 创建以当天日志存放目录
            current_date = time.strftime('%Y-%m-%d', time.localtime())
            current_date_dir_path = CONST.Path.DirPath.Logs.joinpath(current_date)
            if not current_date_dir_path.exists():
                current_date_dir_path.mkdir(parents=True, exist_ok=True)

            # 创建文件流处理器
            for level in _LEVEL_FILE_HANDLES:
                file_handle = logging.FileHandler(current_date_dir_path.joinpath(f'{ level.upper() }.log'))
                file_handle.setFormatter(_LOG_OUTPUT_STRUCTURE)
                file_handle.setLevel(level.upper())
                self._logger.addHandler(file_handle)

            # 创建默认流处理器
            base_handle = logging.StreamHandler()
            base_handle.setFormatter(_LOG_OUTPUT_STRUCTURE)
            base_handle.setLevel(CONFIG.log_level_default.upper())
            self._logger.addHandler(base_handle)

        except BaseException as error:
            raise AwakenLogCreationError(error)


    def out_map(self, level: str, message: str):
        """ 
        [ 映射日志 ]

        ---
        描述:
            根据传递的 level 映射对应等级日志打印。

        ---
        参数:
            level   { str } : 日志等级
            message { str } : 输出的日志信息

        ---
        示例:
            >>> # 映射 error 日志, 等价于 Log.error('message')
            >>> Log = AwakenLog()
            >>> Log.out_map(level='error', message='message')

        ---
        异常:
            AwakenLogOutputError : 日志输出异常

        """
        try:
            type(self).__dict__[level](self, message)

        except KeyError as error:
            raise AwakenLogOutputError(CONST.Error.AWAKEN_LOG_OUTPUT_ERROR.replace('#LEVEL#', str(error)))


    def debug(self, message: str):
        """
        [ 记录 DEBUG 日志 ]

        ---
        参数:
            message (str) : 输出的日志信息

        """
        self._logger.debug(message)


    def info(self, message: str):
        """
        [ 记录 INFO 日志 ]

        ---
        参数:
            message {str} : 输出的日志信息

        """
        self._logger.info(message)


    def warning(self, message: str):
        """
        [ 记录 WARNING 日志 ]

        ---
        参数:
            message {str} : 输出的日志信息

        """
        self._logger.warning(message)


    def error(self, message: str):
        """
        [ 记录 ERROR 日志 ]

        ---
        参数:
            message {str} : 输出的日志信息

        """

        self._logger.error(message)
        

    def critical(self, message: str):
        """
        [ 记录 CRITICAL 日志 ]

        ---
        参数:
            message {str} : 输出的日志信息

        """
        self._logger.critical(message)


LOG: AwakenLog = AwakenLog()
""" 日志模块实例 """
