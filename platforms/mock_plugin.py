# -*- coding: utf-8 -*-
"""platforms/mock_plugin.py
一个不会打开浏览器的 Mock 插件，用于测试 executor 的工作流。
它会：记录开始/结束并模拟成功。
"""
import time
from core.plugin import PlatformPluginBase
from core.storage import append_event

class MockPlugin(PlatformPluginBase):
    name = 'mock'

    def __init__(self, config=None):
        super().__init__(config or {})

    def open_login(self) -> bool:
        append_event(None, 'mock.open_login', 'noop')
        return True

    def navigate_to_editor(self) -> bool:
        append_event(None, 'mock.navigate_to_editor', 'noop')
        return True

    def upload_and_publish(self, task: dict) -> dict:
        # simulate steps and append events
        tid = task.get('id') or 'unknown'
        append_event(tid, 'mock.start', f"start mock upload for {task.get('image')}")
        time.sleep(1)  # simulate work
        append_event(tid, 'mock.upload', f"uploaded {task.get('image')}")
        time.sleep(0.5)
        append_event(tid, 'mock.publish', 'published successfully')
        return {'success': True, 'reason': 'mock ok'}
