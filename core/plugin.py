# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class PlatformPluginBase(ABC):
    name = "base"

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def open_login(self) -> bool:
        """打开登录（扫码或其他），返回是否已触发登录页"""
        pass

    @abstractmethod
    def navigate_to_editor(self) -> bool:
        """导航到发布编辑器页面（视觉或 DOM）"""
        pass

    @abstractmethod
    def upload_and_publish(self, task: dict) -> dict:
        """执行上传并发布，返回 dict: {success: bool, reason: str} """
        pass
