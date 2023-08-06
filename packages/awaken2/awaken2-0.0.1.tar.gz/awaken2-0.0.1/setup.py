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
@ 模块     : Setup
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    PIP package manager build script.

"""
from setuptools import setup
from setuptools import find_packages


# ----------------------------------------------------------------------------
# 项目属性
# ----------------------------------------------------------------------------
NAME        = 'awaken2'
VERSION     = '0.0.1'
AUTHOR      = 'chenjiancheng'
EMAIL       = 'quinn.7@foxmail.com'
DESCRIPTION = 'Awaken 是以 "关键字驱动" 为中心思想搭建的自动化测试框架。'
KEYWORDS    = ['python', 'testing', 'automation', 'testautomation', 'awaken']
URL         = 'https://gitee.com/catcat7/awaken'

LEGAL_PY_VERSION = [
    'Programming Language :: Python :: 3.10',
]

with open('README.md', 'r', encoding='UTF-8') as file:
    LONG_DESCRIPTION = file.read()

INSTALL_REQUIRES = [
    'playwright',
    'flask',
]


# ----------------------------------------------------------------------------
# 项目配置
# ----------------------------------------------------------------------------
setup(
    name                          = NAME, 
    version                       = VERSION, 
    author                        = AUTHOR, 
    author_email                  = EMAIL, 
    description                   = DESCRIPTION,
    keywords                      = KEYWORDS,
    url                           = URL,
    classifiers                   = LEGAL_PY_VERSION,
    long_description              = LONG_DESCRIPTION, 
    long_description_content_type = 'text/markdown',
    install_requires              = INSTALL_REQUIRES,
    packages                      = find_packages('src'), 
    package_dir                   = {'' : 'src'},

    entry_points = {
        'console_scripts':[
            'awaken = awaken.console_awaken:main',
        ],
    },
)
