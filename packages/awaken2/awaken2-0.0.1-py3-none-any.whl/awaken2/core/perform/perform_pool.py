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
@ 模块     : 静态执行池
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import gc
import psutil

from .pool_runtime import PoolRuntime
from ...baseic.log import LOG
from ...baseic.const import CONST
from ...baseic.config import CONFIG
from ...baseic.decorator import singleton_pattern
from ...kit.engine_agency import EngineAgency
from ...core.interpreter.grammar_parser import AwakenTask


class PerFormPool: ...


@singleton_pattern
class PerFormPool(object):
    """
    [ 静态执行池 ]

    ---
    描述:
        通常用于静态执行多进程任务。

    """

    _debug: bool
    """ 调试模式 """
    _pool_runtime: PoolRuntime
    """ 运行时 """

    def __init__(self, 
        engine_max_count: int = 3,
        task_max_count: int = 50,
        debug: bool = None
    ) -> None:
        """
        [ 静态执行池::初始化 ]

        ---
        参数:
            engine_max_count { int } : 引擎最大数量
            task_max_count   { int } : 任务最大数量
            debug           { bool } : 调试模式

        """
        self._debug = debug if debug else CONFIG.debug
        self._pool_runtime = PoolRuntime(engine_max_count, task_max_count)

        # 创建驱动代理
        for _ in range(engine_max_count):
            self._pool_runtime.engine_queue.put(EngineAgency())
            self._pool_runtime.sign_engine()


    def put_task(self, task: AwakenTask):
        """
        [ 推送到任务队列 ]
        
        ---
        参数:
            task { AwakenTask } : 任务对象

        """
        count = self._pool_runtime.task_queue.qsize()
        max_count = self._pool_runtime.task_queue.maxsize
        if max_count > count:
            self._pool_runtime.task_queue.put(task)

    def running(self):
        """
        [ 运行 ]

        ---
        描述:
            NULL

        """
        # --------------------------------------------------------------------
        # 开始一个监听循环
        # 当运行时的任务队列为空且所有代理引擎都空闲时, 跳出监听循环
        # --------------------------------------------------------------------
        while True:

            if self._pool_runtime.task_queue.qsize() == 0:
                if self._debug: 
                    LOG.info(CONST.Error.PerformPool.TaskQueueConsumedMessage)

                while True:
                    core_count = self._pool_runtime.engine_queue.qsize()
                    if core_count == self._pool_runtime.sign_driver_count:
                        if self._debug:
                            LOG.info(CONST.Error.PerformPool.TaskRunningConsumedMessage)
                        break
                break

            # ----------------------------------------------------------------
            # 调用多进程执行任务
            # 驱动冷启动时会占用大量的 CPU 资源, 为避免因为 CPU 占用率过高导致进程启动异常
            # 每隔 X 秒检查 CPU 占用率, 只有 CPU 占用率少于 X 时才会启动进程
            # ----------------------------------------------------------------
            task = self._pool_runtime.task_queue.get()
            engine = self._pool_runtime.engine_queue.get()
            while True:
                if psutil.cpu_percent(CONFIG.cpu_property_time) <= CONFIG.cpu_property_ceiling:
                    self._pool_runtime.pool.apply_async(func=self._emit, args=[task, engine])
                    break


    def _emit(self, task: AwakenTask, engine: EngineAgency):
        """
        [ 触发工作流 ]
        
        ---
        参数:
            task   { AwakenTask } : 任务对象
            engine { EngineAgency } : 驱动对象

        """
        # 核心执行任务
        engine.start(task)
        # 核心执行完任务后, 放回核心队列等待
        self._pool_runtime.engine_queue.put(engine)
        # 强制 GC 回收垃圾避免内存溢出
        gc.collect()
