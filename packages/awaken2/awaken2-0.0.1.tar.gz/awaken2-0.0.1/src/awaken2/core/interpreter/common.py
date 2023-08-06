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
@ 模块     : 解释器通用方法
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import re


def converting_para_format(para: str):
    """
    [ 转换参数格式 ]

    ---
    描述:
        NULL

    """
    para = str(para)

    # 解析BOOL值
    if para in ['true', 'True', 'TRUE']:
        return True
    if para in ['false', 'False', 'FALSE']:
        return False

    # 解析字符串
    if para[0] in ["'", '"'] and para[-1] in ["'", '"']:
        string_extract = re.findall(r'\'(.*)\'', para)
        if len(string_extract) < 1:
            string_extract = re.findall(r'\"(.*)\"', para)
        if len(string_extract) >= 1:
            return string_extract[0]

    # 解析数字
    try:
        int_extract = float(para)
        if int_extract.is_integer():
            int_extract = int(int_extract)
        return int_extract

    except ValueError:
        return para
