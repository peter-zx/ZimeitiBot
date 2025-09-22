# core/browser.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

class Browser:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    def start(self, headless=False):
        """
        启动 Chrome 浏览器
        :param headless: 是否无头模式
        :return: driver
        """
        service = Service(self.driver_path)
        options = Options()
        options.add_argument("--start-maximized")  # 最大化窗口
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-sandbox")

        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def stop(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get(self, url):
        """访问指定 URL"""
        if self.driver:
            self.driver.get(url)
            time.sleep(2)  # 简短延迟，等待页面加载


# 快捷函数，保持之前 quick_test.py 调用方式
def create_driver(headless=False):
    driver_path = os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe")
    browser = Browser(driver_path)
    return browser.start(headless=headless)
