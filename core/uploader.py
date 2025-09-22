# -*- coding: utf-8 -*-
"""
core/uploader.py
视觉模板匹配 + 点击 + 上传工具（OpenCV + pyautogui + Selenium）
覆盖此文件后，quick_upload_test.py 无需改动（仍调用 Uploader.click_button() / upload_image()）
"""

import time
import os
import cv2
import numpy as np
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By

class Uploader:
    def __init__(self, debug=False):
        """
        debug: 如果 True，会保存截图到当前目录用于调试
        """
        self.debug = debug

    def _screenshot_cv(self):
        """
        用 pyautogui 截屏，然后转换成 opencv BGR 格式的 ndarray
        返回: screen (np.ndarray BGR)
        """
        img = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return screen

    def _match_template(self, template_path, confidence=0.85, grayscale=True, max_results=1):
        """
        在当前屏幕查找模板，返回匹配到的中心坐标列表（x,y）按从强到弱排序。
        若未找到返回空列表。
        """
        if not os.path.exists(template_path):
            print(f"[match_template] 模板文件不存在: {template_path}")
            return []

        screen = self._screenshot_cv()
        template = cv2.imread(template_path)
        if template is None:
            print(f"[match_template] 无法读取模板图片: {template_path}")
            return []

        if grayscale:
            screen_proc = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            template_proc = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            screen_proc = screen
            template_proc = template

        # 如果模板比屏幕大，直接返回
        if template_proc.shape[0] > screen_proc.shape[0] or template_proc.shape[1] > screen_proc.shape[1]:
            print("[match_template] 模板尺寸大于屏幕，跳过")
            return []

        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(screen_proc, template_proc, method)
        # 找到所有满足阈值的位置
        loc = np.where(res >= confidence)
        points = list(zip(*loc[::-1]))  # (x,y) pairs

        # 去重与排序（按 res 值）
        matches = []
        for pt in points:
            x, y = int(pt[0]), int(pt[1])
            h, w = template_proc.shape[0], template_proc.shape[1]
            center_x = x + w // 2
            center_y = y + h // 2
            score = res[y, x]
            matches.append((score, center_x, center_y, w, h))
        if not matches:
            # 找不到确切大于阈值的位置，返回最好的一个（可选）
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > 0.5:  # 保底阈值，便于调试
                x, y = max_loc
                h, w = template_proc.shape[0], template_proc.shape[1]
                return [(x + w//2, y + h//2)]
            return []

        # 按 score 降序
        matches.sort(key=lambda x: x[0], reverse=True)
        centers = [(int(m[1]), int(m[2])) for m in matches[:max_results]]
        if self.debug:
            # 保存调试截图并在匹配点画框
            debug_img = screen.copy()
            for score, cx, cy, w, h in matches[:max_results]:
                cv2.rectangle(debug_img, (int(cx - w//2), int(cy - h//2)), (int(cx + w//2), int(cy + h//2)), (0,255,0), 2)
            debug_out = f"debug_match_{os.path.basename(template_path)}.png"
            cv2.imwrite(debug_out, debug_img)
            print(f"[match_template] debug image saved: {debug_out}")
        return centers

    def click_button(self, template_path, confidence=0.85, grayscale=True, clicks=1):
        """
        在屏幕上寻找模板并点击中心点（pyautogui）。
        返回 True/False。
        """
        print(f"尝试点击按钮: {template_path} (confidence={confidence})")
        centers = self._match_template(template_path, confidence=confidence, grayscale=grayscale, max_results=1)
        if not centers:
            print("未找到模板或置信度不够")
            return False
        x, y = centers[0]
        # 移动并点击（可插入随机偏移以模拟人为操作）
        pyautogui.moveTo(x, y, duration=0.3)
        for _ in range(clicks):
            pyautogui.click()
            time.sleep(0.2)
        time.sleep(0.6)
        print(f"点击完毕: ({x},{y})")
        return True

    def upload_image_via_selenium(self, chromedriver_path, file_path, editor_url=None, input_selector="//input[@type='file']"):
        """
        使用 Selenium 打开编辑器页面（可选）并找到 input[type=file] 用 send_keys 上传文件
        返回 True/False
        """
        if not os.path.exists(file_path):
            print(f"[upload_image_via_selenium] 文件不存在: {file_path}")
            return False

        # 启动 Selenium（如果你已有 driver 管理，这里可改为传入 driver）
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=webdriver.chrome.service.Service(chromedriver_path), options=options)

        try:
            if editor_url:
                driver.get(editor_url)
            time.sleep(2)

            el = driver.find_element(By.XPATH, input_selector)
            el.send_keys(os.path.abspath(file_path))
            print("[upload_image_via_selenium] 已填充文件路径到 input")
            time.sleep(2)
            return driver  # 返回 driver 以便后续用它填写标题/正文/发布并关闭
        except Exception as e:
            print(f"[upload_image_via_selenium] 异常: {e}")
            try:
                driver.quit()
            except:
                pass
            return False

    def upload_image_via_selenium_with_fill(self, chromedriver_path, file_path, title_text="", content_text="",
                                            editor_url=None, input_selector="//input[@type='file']",
                                            title_selector="//input[@id='title' or @name='title']", content_selector="//textarea"):
        """
        综合方法：打开编辑器，上传文件，填标题/正文（尝试通用 selector），并返回 driver（需后续点击发布/关闭）
        """
        driver = self.upload_image_via_selenium(chromedriver_path, file_path, editor_url=editor_url, input_selector=input_selector)
        if not driver:
            return False
        try:
            time.sleep(1)
            # 填写标题（尝试多种 selector）
            try:
                t_el = driver.find_element(By.XPATH, title_selector)
                t_el.clear()
                t_el.send_keys(title_text)
            except Exception:
                pass
            # 填写正文
            try:
                c_el = driver.find_element(By.XPATH, content_selector)
                c_el.clear()
                c_el.send_keys(content_text)
            except Exception:
                pass
            time.sleep(1)
            return driver
        except Exception as e:
            print(f"[upload_image_via_selenium_with_fill] 异常: {e}")
            try:
                driver.quit()
            except:
                pass
            return False
