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
@ 模块     : Baseic.Common
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import os
import hashlib

from pathlib import Path

from .const import CONST


_ENVIRONMENT_VARIABLE = 'USERPROFILE'
_PLAYWRIGHT_PATH = Path(os.environ[_ENVIRONMENT_VARIABLE]).joinpath('AppData\Local\ms-playwright')


def check_browser_driver_is_installed():
    """
    [ 检查浏览器驱动是否安装 ]

    ---
    描述:
        NULL

    """
    browser_list = ['chromium', 'firefox', 'webkit']
    local_browser_list = []

    # 检查本地 playwright 环境是否安装浏览器驱动
    if _ENVIRONMENT_VARIABLE in os.environ:
        for dir_path in _PLAYWRIGHT_PATH.glob('*'):
            local_browser_list.append(dir_path.stem.split('-')[0])

        # 如果浏览器驱动不存在本地则下载
        for browser_name in browser_list:
            if browser_name not in local_browser_list:
                print(f'正在下载浏览器驱动 :: { browser_name }')
                os.system(f'playwright install { browser_name }')


def create_program_runtime_dependency_files():
    """
    [ 创建程序运行时的依赖文件 ]

    ---
    描述:
        NULL
    
    """
    for path in [
        CONST.Path.DirPath.Data,
        CONST.Path.DirPath.Logs,
        CONST.Path.DirPath.BaseCode,
    ]:
        path.mkdir(parents=True, exist_ok=True)

    for path in [
        CONST.Path.FilePath.Config,
        CONST.Path.FilePath.Database,
    ]:
        path.touch(mode=0o777, exist_ok=True)


def md5_encrypt(string: str):
    """
    [ MD5加密 ]
    
    ---
    描述:
        NULL

    ---
    参数:
        string { str } : 需要加密的字符串。

    """
    file_md5hash = hashlib.md5(string.encode('UTF-8'))
    return file_md5hash.hexdigest()
