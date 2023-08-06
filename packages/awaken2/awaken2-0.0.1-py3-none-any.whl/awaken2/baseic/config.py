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
@ 模块     : 全局静态配置器
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os
import yaml

from .const import CONST
from .keyword import KEYWORD
from .decorator import singleton_pattern


class AwakenConfig: ...


@singleton_pattern
class AwakenConfig(object):
    """
    [ 全局静态配置器 ]

    ---
    描述:
        NULL

    """

    _config_cache_data: dict
    """ 配置缓存数据 """
    _debug: bool
    """ 调试模式 """
    _engine_queue_max_count: int
    """ 驱动队列阈值 """
    _task_queue_max_count: int
    """ 任务队列阈值 """
    _cpu_property_time: int
    """ CPU资源检查时间 """
    _cpu_property_ceiling: int
    """ CPU资源检查阈值 """
    _log_level_floor: str
    """ 日志等级下限 """
    _log_level_default: str
    """ 日志等级默认 """


    def __init__(self):
        """ 
        [ 全局静态配置器 :: 实例化 ] 

        ---
        描述:
            NULL

        """
        self.read_configuration_file()


    @property
    def debug(self):
        """
        [ 获取调试模式 ]

        ---
        描述:
            NULL

        """
        return self._debug


    @property
    def engine_queue_max_count(self):
        """
        [ 获取驱动队列阈值 ]

        ---
        描述:
            NULL

        """
        return self._engine_queue_max_count


    @property
    def task_queue_max_count(self):
        """
        [ 获取任务队列阈值 ]

        ---
        描述:
            NULL

        """
        return self._task_queue_max_count


    @property
    def cpu_property_time(self):
        """
        [ 获取CPU资源检查时间 ]

        ---
        描述:
            NULL

        """
        return self._cpu_property_time


    @property
    def cpu_property_ceiling(self):
        """
        [ 获取CPU资源检查阈值 ]

        ---
        描述:
            NULL

        """
        return self._cpu_property_ceiling


    @property
    def log_level_floor(self):
        """
        [ 获取日志等级下限 ]

        ---
        描述:
            NULL

        """
        return self._log_level_floor


    @property
    def log_level_default(self):
        """
        [ 获取日志等级默认 ]

        ---
        描述:
            NULL

        """
        return self._log_level_default


    def read_configuration_file(self):
        """
        [ 读取配置文件 ]

        ---
        描述:
            NULL

        """
        self._config_cache_data = {}

        # 配置文件如果为空则创建写入缺省配置数据
        if os.path.getsize(CONST.Path.FilePath.Config) == 0:
            self._write_default_data()

        with open(file=CONST.Path.FilePath.Config, mode='r', encoding='UTF-8') as file:
            self._config_cache_data      = yaml.load(file, Loader=yaml.FullLoader)
            self._debug                  = self._config_cache_data[KEYWORD.Common.Config.Debug]
            self._engine_queue_max_count = self._config_cache_data[KEYWORD.Common.Config.EngineQueueMaxCount]
            self._task_queue_max_count   = self._config_cache_data[KEYWORD.Common.Config.TaskQueueMaxCount]
            self._cpu_property_time      = self._config_cache_data[KEYWORD.Common.Config.CpuPropertyTime]
            self._cpu_property_ceiling   = self._config_cache_data[KEYWORD.Common.Config.CpuPropertyCeiling]
            self._log_level_floor        = self._config_cache_data[KEYWORD.Common.Config.LogLevelFloor]
            self._log_level_default      = self._config_cache_data[KEYWORD.Common.Config.LogLevelDefault]


    def _write_default_data(self):
        """
        [ 写入缺省数据 ]

        """
        self._config_cache_data[KEYWORD.Common.Config.Debug]               = True
        self._config_cache_data[KEYWORD.Common.Config.EngineQueueMaxCount] = 3
        self._config_cache_data[KEYWORD.Common.Config.TaskQueueMaxCount]   = 50
        self._config_cache_data[KEYWORD.Common.Config.CpuPropertyTime]     = 2
        self._config_cache_data[KEYWORD.Common.Config.CpuPropertyCeiling]  = 30
        self._config_cache_data[KEYWORD.Common.Config.LogLevelFloor]       = CONST.Common.LogLevel.Debug
        self._config_cache_data[KEYWORD.Common.Config.LogLevelDefault]     = CONST.Common.LogLevel.Info
        self.dump()


    def dump(self):
        """
        [ 存储配置 ]

        """
        with open(file=CONST.Path.FilePath.Config, mode='w', encoding='UTF-8') as file:
            yaml.dump(self._config_cache_data, file, allow_unicode=True)


    def set_debug(self, state: bool):
        """
        [ 设置调试模式 ]
        
        ---
        参数:
            state { bool } : 调试模式

        """
        self._debug = state
        self._config_cache_data[KEYWORD.Common.Config.Debug] = state


    def set_engine_queue_max_count(self, number: int):
        """
        [ 设置驱动队列阈值 ]
        
        ---
        参数:
            number { int } : 数量

        """
        self._engine_queue_max_count = number
        self._config_cache_data[KEYWORD.Common.Config.EngineQueueMaxCount] = number


    def set_task_queue_max_count(self, number: int):
        """
        [ 设置任务队列阈值 ]
        
        ---
        参数:
            number { int } : 数量

        """
        self._task_queue_max_count = number
        self._config_cache_data[KEYWORD.Common.Config.TaskQueueMaxCount] = number


    def set_cpu_property_time(self, property_time: int):
        """
        [ 设置CPU资源检查时间 ]
        
        ---
        参数:
            property_time { int } : 检测时间

        """
        self._cpu_property_time = property_time
        self._config_cache_data[KEYWORD.Common.Config.CpuPropertyTime] = property_time


    def set_cpu_property_ceiling(self, capacity_size: int):
        """
        [ 设置CPU资源检查阈值 ]
        
        ---
        参数:
            capacity_size { int } : 检查阈值

        """
        self._cpu_property_ceiling = capacity_size
        self._config_cache_data[KEYWORD.Common.Config.CpuPropertyCeiling] = capacity_size


    def set_log_level_floor(self, log_level: str):
        """
        [ 设置日志等级下限 ]

        ---
        参数:
            log_level { str } : 日志等级

        """
        try:
            self._log_level_floor = CONST.Common.LogLevel.__dict__[log_level]

        except KeyError:
            self._log_level_floor = CONST.Common.LogLevel.Debug

        self._config_cache_data[KEYWORD.Common.Config.Debug] = self._log_level_floor


    def set_log_level_default(self, log_level: str):
        """
        [ 设置日志等级默认 ]

        ---
        参数:
            log_level { str } : 日志等级

        """
        try:
            self.log_level_default = CONST.Common.LogLevel.__dict__[log_level]

        except KeyError:
            self.log_level_default = CONST.Common.LogLevel.Info

        self._config_cache_data[KEYWORD.Common.Config.Debug] = self.log_level_default


CONFIG: AwakenConfig = AwakenConfig()
""" 静态配置实例 """
