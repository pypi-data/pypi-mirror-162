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
@ 模块     : WEB驱动引擎
@ 作者     : chenjiancheng
@ 邮箱     : quinn.7@foxmail.com
@ 编写时间 : 2022-08-10

@ 模块描述 :
    NULL

"""
import time
import asyncio
from typing import Any

from pathlib import Path

from ...baseic.const import CONST
from ...baseic.error import AwakenWebEngineError


class WebEngine: ...


class WebEngine:
    """
    [ WEB驱动引擎 ]

    ---
    描述:
        NULL

    """

    _playwright: Any
    """ playwright 对象 """
    _browser_map: dict
    """ 浏览器类型映射字典 """
    _browser = None
    """ 浏览器进程 """
    _context = None
    """ 浏览器上下文 """
    _page = None
    """ 浏览器页面 """


    def __init__(self, playwright) -> None:
        """
        [ WEB驱动引擎 :: 初始化 ]

        ---
        描述:
            NULL

        """
        self._playwright = playwright
        self._browser_map = {
            CONST.Type.Browser.Webkit : self._playwright.webkit,
            CONST.Type.Browser.Firefox : self._playwright.firefox,
            CONST.Type.Browser.Chromium : self._playwright.chromium,
        }


    async def _browser_start(
        self, 
        browser_type=CONST.Type.Browser.Chromium, 
        headless=False
    ):
        """ 
        [ 启动浏览器 ]

        ---
        描述:
            根据传入的浏览器类型启动对象浏览器进程。

        ---
        参数:
            browser_type { str } : 浏览器类型。
            headless    { bool } : 是否以无头模式运行。

        """
        # 如果浏览器类型不存在, 则使用默认的 Chromium 浏览器
        if browser_type not in self._browser_map.keys():
            browser_type = CONST.Type.Browser.Chromium

        # 创建浏览器实例不存在则创建
        if not self._browser:
            self._browser = await self._browser_map[browser_type].launch(headless=headless)
            self._context = await self._browser.new_context()


    async def _page_start(self):
        """
        [ 启动页面 ]

        ---
        描述:
            浏览器进程启动页面实例。

        """
        self._page = await self._context.new_page()


    async def _page_close(self):
        """
        [ 关闭页面 ]
    
        ---
        描述:
            浏览器进程关闭页面实例。
        
        """
        await self._page.close()
        self._page = None


    async def _exit(self):
        """
        [ 退出浏览器 ]

        ---
        描述:
            关闭页面、上下文、浏览器对象。
        
        """
        if self._page:
            await self._page.close()
            await self._context.close()
            await self._browser.close()
        self._page = None
        self._context = None
        self._browser = None


    async def new_context(self):
        """
        [ 重置上下文 ]

        ---
        描述:
            重置浏览器的上下文, 然后重新打开一个新页面。
        
        """
        if self._page:
            await self._page.close()
            self._page = None

        await self._context.close()
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()


    async def get_page_name(self) -> str:
        """
        [ 页面名称 ]

        ---
        描述:
            获取当前页面中的 Title 属性。

        ---
        返回:
            str : 当前页面的名称

        """
        return await self._page.title()


    async def get_element_count(self, element: str, eid=1) -> int:
        """
        [ 获取元素数量 ]

        ---
        描述:
            获取当前页面中能够定位到的元素数量。

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        ---
        返回:
            int : 元素数量

        """
        _, count = await self._locator_elements(element, eid)
        return count


    async def get_element_text(self, element: str, eid=1) -> str:
        """
        [ 获取元素的文本 ]

        ---
        描述:
            获取当前页面中定位元素的文本。

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        ---
        返回:
            str : 元素的文本

        """
        element, _ = await self._locator_elements(element, eid)
        element_text = await element.text_content()
        return element_text.strip()

    
    async def get_input_value(self, element: str, eid=1) -> str:
        """
        [ 获取Input控件中的值 ]

        ---
        描述:
            NULL

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        ---
        返回:
            str : 元素的文本

        """
        element, _ = await self._locator_elements(element, eid)
        element_text = await element.input_value()
        return element_text

    
    async def get_attribute(self, name: str, element: str, eid=1) -> str | int:
        """
        [ 获取元素的属性值 ]

        ---
        描述:
            NULL

        ---
        参数:
            name    { str } : 需获取值的属性名称
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        ---
        返回:
            str | int : 元素的属性值

        """
        element, _ = await self._locator_elements(element, eid)
        return await element.get_attribute(name)

    
    async def set_window_size(self, width: int, height: int):
        """
        [ 设置浏览器尺寸 ]

        ---
        描述:
            NULL

        ---
        参数:
            width { int }  : 宽度
            height { int } : 长度

        """
        size = {
            'width' : int(width),
            'height': int(height)
        }
        await self._page.set_viewport_size(size)


    async def goto(self, url: str):
        """
        [ 页面跳转至 URL ]

        ---
        描述:
            NULL

        ---
        参数:
            url { str } : 跳转目标 URL 地址

        """
        await self._page.goto(url)


    async def back(self):
        """
        [ 后退 ]

        ---
        描述:
            NULL

        """
        await self._page.go_back()


    async def forward(self):
        """
        [ 前进 ]

        ---
        描述:
            NULL

        """
        await self._page.go_forward()

    
    async def reload(self):
        """
        [ 刷新 ]

        ---
        描述:
            NULL
            
        """
        await self._page.reload()


    async def send(self, key: str, element: str, eid=1):
        """
        [ 输入文本 ]

        ---
        描述:
            该函数期望的目标控件是 Input。

        ---
        参数:
            key     { str } : 输入文本的值
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        """
        element, _ = await self._locator_elements(element, eid)
        await element.fill(key)


    async def click(self, element: str, eid=1):
        """
        [ 鼠标单击 ]

        ---
        描述:
            NULL

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        """
        element, _ = await self._locator_elements(element, eid)
        await element.click()


    async def dbl_click(self, element, eid=1):
        """
        [ 鼠标双击 ]

        ---
        描述:
            NULL

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        """
        element, _ = await self._locator_elements(element, eid)
        await element.dblclick()


    async def drag_to(self, element1: str, element2: str, eid=1):
        """
        [ 鼠标拖拽 ]

        ---
        描述:
            模拟鼠标拖拽行为, 将元素1拖拽至元素2, 并且松开鼠标。

        ---
        参数:
            element1 { str } : 元素1定位描述字符
            element2 { str } : 元素2定位描述字符
            eid      { int } : 元素下标

        """
        element1, _ = await self._locator_elements(element1, eid)
        element2, _ = await self._locator_elements(element2, 1)
        await element1.drag_to(element2)


    async def hover(self, wait, element: str, eid=1):
        """
        [ 鼠标悬停 ]

        ---
        描述:
            NULL

        ---
        参数:
            wait    { int } : 悬停时间
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        """
        element, _ = await self._locator_elements(element, eid)
        await element.hover()
        await asyncio.sleep(wait)


    async def popup_ok(self, element: str, eid=1, text=''):
        """
        [ 弹窗确定 ]

        ---
        描述:
            点击一个绑定了弹窗事件的按钮元素, 然后静默确认该弹窗, 如果该弹窗存在输入框, 可通过参数 text 来填充。

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标
            text    { str } : 输入文本

        """
        # 弹窗处理函数
        async def event(dialog):
            global temporary_text_register
            temporary_text_register = dialog.message
            await dialog.accept(text)

        # 绑定弹窗处理事件
        self._page.once('dialog', event)
        element, _ = await self._locator_elements(element, eid)
        await element.click()
        return temporary_text_register


    async def popup_no(self, element: str, eid=1):
        """
        [ 弹窗取消 ]

        ---
        描述:
            点击一个绑定了弹窗事件的按钮元素, 然后静默取消该弹窗。

        ---
        参数:
            element { str } : 元素定位描述字符
            eid     { int } : 元素下标

        """
        # 弹窗处理函数
        async def event(dialog):
            global temporary_text_register
            temporary_text_register = dialog.message
            await dialog.dismiss()

        # 绑定弹窗处理事件
        self._page.once('dialog', event)
        element, _ = await self._locator_elements(element, eid)
        await element.click()
        return temporary_text_register


    async def upload(self, element: str, file_path: str, eid=1):
        """
        [ 上传文件 ]

        ---
        描述:
            点击一个绑定了文件上传事件的按钮元素, 然后静默处理该事件。

        ---
        参数:
            element   { str } : 元素定位描述字符
            file_path { str } : 文件完整路径
            eid       { int } : 元素下标

        """
        # 监听文件选择器对象
        self._page.once('filechooser', lambda _: ...)
        async with self._page.expect_file_chooser() as chooser_object:
            element, _ = await self._locator_elements(element, eid)
            await element.click()

        chooser_object = await chooser_object.value
        await chooser_object.set_files(file_path)


    async def download(self, element: str, file_path: str, eid=1):
        """
        [ 下载文件 ]

        ---
        描述:
            点击一个绑定了文件下载事件的按钮元素, 然后静默处理该事件。

        ---
        参数:
            element { str } : 元素定位描述字符
            file_path { str } : 文件保存路径
            eid { int } : 元素下标

        """
        # 监听下载对象
        self._page.once('download', lambda _: ...)
        async with self._page.expect_download() as download_object:
            element, _ = await self._locator_elements(element, eid)
            await element.click()
        download_object = await download_object.value
        await download_object.save_as(file_path)
        return file_path

    
    async def save_png(self, save_path: str):
        """
        [ 保存 PNG 图片 ]

        ---
        参数:
            save_path { str } : 图片保存路径

        """
        png_bytes = await self._page.screenshot()
        suffix = '.png'
        if save_path[-4:] != suffix:
            save_path = ''.join([save_path, suffix])
        save_path = Path(save_path)
        save_path.touch(0o777)
        save_path.write_bytes(png_bytes)
        return save_path.resolve()


    async def dispatch_event(self, element, event_name):
        await self._page.dispatch_event(element, event_name)


    async def java_script(self, expression, args):
        return await self._page.evaluate(expression, args)


    async def _locator_elements(self, element: str, eid: int):
        """
        [ 定位元素 ]

        ---
        描述:
            定位当前页面的所有符合预期的元素对象。

        ---
        参数:
            element { str } : 元素定位方式
            eid     { int } : 元素ID

        ---
        返回:
            tuple(Any | int) : 元素对象 | 元素数量

        """
        element_count: int
        retries_number = 5  # 元素重试次数
        retries_sleep  = 1  # 元素重试间隔时间

        try:
            for _ in range(retries_number):
                result = self._page.locator(element)
                element_count = await result.count()
                if element_count < 1:
                    time.sleep(retries_sleep)
                    continue
                else:
                    break
                
            if element_count == 0:
                raise BaseException

        except BaseException:
            raise AwakenWebEngineError(f'无法定位到元素 :: { element } !')
                
        try:
            # 如果 eid 大于元素数量则抛出异常
            if element_count < eid: 
                raise BaseException
            else:
                return result.nth(eid - 1), element_count

        except BaseException:
            raise AwakenWebEngineError(f'EID 超出元素对象数量, 无法应用 !')
