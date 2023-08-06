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
@ 模块     : 关键字驱动自动化框架
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    Awaken 是以 "关键字驱动" 为中心思想搭建的自动化测试框架。\n
    关键字驱动又称为表格驱动, 它分离了编码与用例, 使得非技术人员也能很容易的理解与编写自动化脚本。

"""
from .baseic.common import check_browser_driver_is_installed
from .baseic.common import create_program_runtime_dependency_files


# ----------------------------------------------------------------------------
# 调用框架时检验环境
# ----------------------------------------------------------------------------
check_browser_driver_is_installed()
create_program_runtime_dependency_files()
