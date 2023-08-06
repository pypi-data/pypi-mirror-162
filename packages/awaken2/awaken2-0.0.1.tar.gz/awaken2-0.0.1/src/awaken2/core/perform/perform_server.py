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
@ 模块     : 服务执行池
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import gc
import psutil

from flask import jsonify
from flask import Blueprint
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer

from .pool_runtime import PoolRuntime
from ...baseic.log import LOG
from ...baseic.const import CONST
from ...baseic.config import CONFIG
from ...server.api.awaken_app import AwakenApp
from ...kit.engine_agency import EngineAgency
from ...core.interpreter.grammar_parser import AwakenTask


class PerformServer: ...


_POOL_RUNTIME: PoolRuntime = PoolRuntime()
""" POOL运行时 """

# 创建驱动代理
for _ in range(CONFIG.engine_queue_max_count):
    _POOL_RUNTIME.engine_queue.put(EngineAgency())
    _POOL_RUNTIME.sign_engine()

# ----------------------------------------------------------------------------
# 临时测试依赖
# ----------------------------------------------------------------------------
from ...server.api.server_request_handler import URL_PREFIX


BLUEPRINT_AWAKEN = Blueprint('awaken', __name__)
""" [ Awaken 任务测试接口蓝图 ] """


@BLUEPRINT_AWAKEN.route(f'{ URL_PREFIX }/awaken/test', methods=['GET'])
def tasks():
    from ..interpreter.grammar_parser import GrammarParser
    gp = GrammarParser()
    task = gp.parsing('D:/Code/awaken/test/task.awaken-web')
    _POOL_RUNTIME.task_queue.put(task)

    return jsonify({
        'code': 0,
        'result': {
            'data': '测试任务已接收',
        },
        'message': 'ok',
        'type': 'success'
    })
# ----------------------------------------------------------------------------


class PerformServer(object):
    """
    [ 执行服务 ]

    ---
    描述:
        开启时, 将在本地挂起一个执行池进程与 WebAPI 服务。

    """

    _debug: bool
    """ 调试模式 """

    def running(self, port: int = 3700, debug: bool = None):
        """
        [ 运行 ]

        ---
        参数:
            port  { int } : 服务端口号, 默认为 3700
            debug { bool } : 调试模式

        """
        self._debug = debug if debug else CONFIG.debug
        _POOL_RUNTIME.pool.apply_async(func=self.monitor)
        
        app = AwakenApp()
        app.load_blueprint(BLUEPRINT_AWAKEN)
        
        http_server = HTTPServer(WSGIContainer(app.living))
        http_server.listen(port)

        if self._debug:
            LOG.info(CONST.Error.PerformPool.ServerRunningMessage.replace('#PORT#', port))

        IOLoop.current().start()


    def monitor(self):
        """
        [ 监听进程 ]
        
        ---
        描述:
            监听来自 POOL 运行时的队列信息。

        """
        if self._debug:
            LOG.info(CONST.Error.PerformPool.ListeningProcessStarted)

        while True:

            # ----------------------------------------------------------------
            # 调用多进程执行任务
            # 驱动冷启动时会占用大量的 CPU 资源, 为避免因为 CPU 占用率过高导致进程启动异常
            # 每隔 X 秒检查 CPU 占用率, 只有 CPU 占用率少于 X 时才会启动进程
            # ----------------------------------------------------------------
            task = _POOL_RUNTIME.task_queue.get()
            engine = _POOL_RUNTIME.engine_queue.get()
            while True:
                if psutil.cpu_percent(CONFIG.cpu_property_time) <= CONFIG.cpu_property_ceiling:
                    _POOL_RUNTIME.pool.apply_async(func=self._emit, args=[task, engine])
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
        task.start(engine)
        # 核心执行完任务后, 放回核心队列等待
        _POOL_RUNTIME.engine_queue.put(engine)
        # 强制 GC 回收垃圾避免内存溢出
        gc.collect()
