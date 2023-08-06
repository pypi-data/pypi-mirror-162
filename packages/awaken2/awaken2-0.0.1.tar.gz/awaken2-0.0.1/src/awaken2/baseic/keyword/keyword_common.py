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
@ 模块     : 通用字段关键字
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL
    
"""


class Config: ...


class Config:
    """
    [ 通用字段关键字索引 :: 配置 ]

    ---
    描述: 
        配置相关的字段。
        
    """

    Debug = 'debug'
    """ 调试模式 """

    EngineQueueMaxCount = 'engine_queue_max_count'
    """ 驱动队列阈值 """

    TaskQueueMaxCount = 'task_queue_max_count'
    """ 任务队列阈值 """

    CpuPropertyTime = 'cpu_property_time'
    """ CPU资源检查时间 """

    CpuPropertyCeiling = 'cpu_property_ceiling'
    """ CPU资源检查阈值 """

    LogLevelFloor = 'log_level_floor'
    """ 日志等级下限 """

    LogLevelDefault = 'log_level_default'
    """ 日志等级默认 """
