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
[ API驱动引擎 ]

"""
import time
import requests

from ...baseic.const import CONST
from ...baseic.log import LOG
from ...baseic.error import AwakenApiEngineError


class ApiEngine: ...


class ApiEngine(object):
    """
    [ API驱动引擎 ]

    ---
    描述:
        NULL

    """

    _headers: dict
    """ 请求头 """


    def __init__(self) -> None:
        """
        [ API驱动引擎 :: 初始化 ]

        ---
        描述:
            NULL

        """
        self._headers = {}


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


    def sleep(self, wait: int):
        """
        [ 停滞等待 ]

        ---
        描述:
            NULL
        
        ---
        参数:
            wait { int } : 等待时长, 单位秒。
        
        """
        time.sleep(int(wait))


    def headers_add(self, key: str, value: str):
        """
        [ 请求头新增 ]

        ---
        描述:
            NULL

        """
        self._headers.update({key : value})


    def set_token(self, token: str):
        """
        [ 设置登录态 ]

        ---
        描述:
            NULL

        """
        self._headers.update({'Authorization' : f'Bearer {token}'})


    def get(self, url: str, data: dict = None):
        """
        [ GET 请求 ]

        ---
        描述:
            NULL

        """
        result = requests.get(url=url, params=data, headers=self._headers)
        return result.json()


    def post(self, url: str, data: dict = None):
        """
        [ POST 请求 ]

        ---
        描述:
            NULL
            
        """
        result = requests.post(url=url, data=data, headers=self._headers)
        return result.json()
