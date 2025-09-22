# -*- coding: utf-8 -*-
import time
from selenium.webdriver.common.by import By

class XiaoHongShu:
    def __init__(self, driver):
        self.driver = driver
        self.login_url = "https://creator.xiaohongshu.com/login"

    def login_scan(self):
        self.driver.get(self.login_url)
        print("请扫码登录小红书...")
        # 给用户时间扫码登录
        time.sleep(20)
        print("扫码登录结束，可继续执行上传操作")
