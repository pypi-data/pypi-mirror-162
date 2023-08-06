# Copyright 2022. quinn.7@foxmail.com All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""
[ 池运行时 ]

"""
from multiprocessing.pool import ThreadPool
from multiprocessing.dummy import Pool
from multiprocessing.dummy import Lock
from multiprocessing.dummy import Queue
from multiprocessing.dummy import Manager

from ...baseic.config import CONFIG


class PoolRuntime(object):
    """
    [ POOL 运行时 ]

    """

    _pool: ThreadPool
    """ 进程池 """
    _state: bool
    """ 运行状态 """
    _engine_max_count: int
    """ 引擎最大数量 """
    _task_max_count: int
    """ 任务最大数量 """
    _sign_engine_count: int
    """ 注册的驱动数量 """
    _engine_queue: Queue
    """ 引擎队列 """
    _task_queue: Queue
    """ 任务队列 """
    _state_lock: Lock
    """ 运行状态互斥锁 """
    _engine_queue_lock: Lock
    """ 引擎队列互斥锁 """
    _task_queue_lock: Lock
    """ 任务队列互斥锁 """


    def __init__(self, 
        engine_max_count: int = CONFIG.engine_queue_max_count, 
        task_max_count: int = CONFIG.task_queue_max_count
    ) -> None:
        """
        [ POOL 运行时 ]
        
        ---
        参数:
            engine_max_count { int } : 引擎最大数量
            task_max_count   { int } : 任务最大数量

        """
        self._engine_max_count = engine_max_count
        self._task_max_count = task_max_count

        manager: Manager = Manager()
        self._pool = Pool(self._engine_max_count + 1)
        self._state = False
        self._sign_engine_count = 0
        self._engine_queue = manager.Queue(maxsize=self._engine_max_count)
        self._task_queue = manager.Queue(maxsize=self._task_max_count)
        self._state_lock = manager.Lock()
        self._engine_queue_lock = manager.Lock()
        self._task_queue_lock = manager.Lock()


    @property
    def pool(self) -> ThreadPool:
        """
        [ 进程池 ]

        """
        return self._pool


    @property
    def state(self) -> bool:
        """
        [ 运行状态 ]

        """
        with self._state_lock:
            return self._state


    @property
    def engine_max_count(self) -> int:
        """
        [ 驱动队列最大值 ]

        """
        return self._engine_max_count


    @property
    def task_max_count(self) -> int:
        """
        [ 任务队列最大值 ]

        """
        return self._task_max_count


    @property
    def sign_driver_count(self) -> int:
        """
        [ 注册的核心数量 ]

        """
        return self._sign_engine_count


    @property
    def engine_queue(self) -> Queue:
        """
        [ 核心队列 ]

        """
        with self._engine_queue_lock:
            return self._engine_queue


    @property
    def task_queue(self) -> Queue:
        """
        [ 任务队列 ]

        """
        with self._task_queue_lock:
            return self._task_queue


    def set_state(self, state: bool):
        """
        [ 设置运行状态 ]
        
        ---
        参数:
            state { bool } : 运行状态

        """
        with self._state_lock:
            self._state = state


    def sign_engine(self):
        """
        [ 注册引擎 ]

        """
        self._sign_engine_count += 1
