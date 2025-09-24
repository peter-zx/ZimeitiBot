from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import time
import json


# 可按需导入
import cv2
import pyautogui
from dateutil import parser as dtparser


# DOM 模式预留
try:
from selenium import webdriver
from selenium.webdriver.common.by import By
except Exception:
webdriver = None
By = None


@dataclass
class Step:
name: str
action_type: str # click_template | type_template | click_selector | type_selector | wait
template: str | None = None
selector: str | None = None # XPath/CSS
fill_from: str | None = None # title|content|media
extra: dict | None = None


class VisualExecutor:
def __init__(self, templates_root: Path):
self.templates_root = Path(templates_root)
pyautogui.PAUSE = 0.3


def _match_template(self, template_rel_path: str, confidence: float=0.82):
img_path = self.templates_root / template_rel_path
screenshot = pyautogui.screenshot()
screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
tpl = cv2.imread(str(img_path))
res = cv2.matchTemplate(screenshot_cv, tpl, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
if max_val < confidence:
raise RuntimeError(f"Template not found: {template_rel_path}, score={max_val:.2f}")
h, w = tpl.shape[:2]
center = (max_loc[0] + w//2, max_loc[1] + h//2)
return center


def click_template(self, template_rel_path: str):
x, y = self._match_template(template_rel_path)
pyautogui.moveTo(x, y)
pyautogui.click()


def type_template(self, template_rel_path: str, text: str):
x, y = self._match_template(template_rel_path)
pyautogui.click(x, y)
pyautogui.typewrite(text, interval=0.02)


class Runner:
def __init__(self, platforms_json: Path, templates_root: Path):
self.platforms_json = Path(platforms_json)
self.templates_root = Path(templates_root)
self.visual = VisualExecutor(self.templates_root)
raise NotImplementedError(step.action_type)