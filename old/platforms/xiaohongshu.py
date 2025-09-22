# platforms/xiaohongshu.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from utils.helpers import human_sleep
import time

logger = get_logger("xiaohongshu")

class XiaoHongShu:
    def __init__(self, driver, timeout: int = 20):
        self.driver = driver
        self.timeout = timeout
        self.home = "https://www.xiaohongshu.com"
        self.creator = "https://creator.xiaohongshu.com"

    def open_login_page(self):
        url = self.creator + "/login"
        try:
            self.driver.get(url)
        except Exception:
            self.driver.get(self.creator)
        logger.info("打开小红书创作者登录页：%s", url)

    def wait_for_manual_login(self, check_fn=None, timeout: int = 300):
        logger.info("等待人工登录，请在浏览器扫码或手动登录。")
        start = time.time()
        if check_fn:
            while time.time() - start < timeout:
                try:
                    if check_fn(self.driver):
                        logger.info("检测到登录完成。")
                        return True
                except Exception:
                    pass
                time.sleep(2)
            logger.warning("等待登录超时。")
            return False
        else:
            input("请在浏览器完成登录，完成后按回车继续...")
            return True

    def try_find(self, by, selector, wait_first=True, timeout=None):
        t = timeout or self.timeout
        if wait_first:
            try:
                return WebDriverWait(self.driver, t).until(EC.presence_of_element_located((by, selector)))
            except Exception:
                return None
        else:
            try:
                return self.driver.find_element(by, selector)
            except Exception:
                return None

    def navigate_to_create_editor(self):
        logger.info("尝试导航到发布编辑器（直接跳转或视觉点击）。")
        possible = [
            self.creator + "/editor",
            self.creator + "/create",
            "https://www.xiaohongshu.com/explore"
        ]
        for u in possible:
            try:
                self.driver.get(u)
                human_sleep(1.0, 2.0)
                el = self._find_file_input(wait=False)
                if el:
                    logger.info("通过跳转找到编辑器页面：%s", u)
                    return True
            except Exception:
                continue

        # 视觉点击入口备选
        selectors = [
            (By.XPATH, "//button[contains(., '创作') or contains(., '写笔记') or contains(., '发布')]"),
            (By.CSS_SELECTOR, "a[href*='create'], a[href*='editor']"),
            (By.CSS_SELECTOR, "button.publish, button.create")
        ]
        for by, sel in selectors:
            try:
                el = self.try_find(by, sel, wait_first=True, timeout=3)
                if el:
                    try:
                        el.click()
                        human_sleep(1.0, 2.0)
                        if self._find_file_input(wait=False):
                            logger.info("通过视觉点击进入编辑器（selector=%s）", sel)
                            return True
                    except Exception:
                        continue
            except Exception:
                continue

        logger.warning("未能自动定位编辑器入口，请手动在浏览器打开编辑器页面。")
        return False

    def _find_file_input(self, wait=True, timeout=8):
        try:
            if wait:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
            else:
                return self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        except Exception:
            return None

    def upload_one_file(self, file_path: str, caption: str = "", title: str = "") -> bool:
        logger.info("开始上传文件：%s", file_path)
        input_el = self._find_file_input(wait=True, timeout=8)
        if not input_el:
            ok = self.navigate_to_create_editor()
            if not ok:
                logger.error("无法进入编辑器页面，上传失败。")
                return False
            input_el = self._find_file_input(wait=True, timeout=8)
            if not input_el:
                logger.error("仍然找不到上传 input[type=file]。")
                return False

        try:
            input_el.send_keys(file_path)
            logger.info("已填充文件路径到 input[type=file]，等待媒体预览...")
        except Exception as e:
            logger.exception("send_keys 上传失败: %s", e)
            return False

        human_sleep(1.5, 3.0)

        # 填写描述/标题（优先 textarea）
        try:
            ta = self.driver.find_element(By.CSS_SELECTOR, "textarea")
            ta.clear()
            ta.send_keys(caption or title or "自动上传")
            logger.info("已在 textarea 填写文案。")
        except Exception:
            try:
                ce = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                ce.click()
                ce.send_keys(caption or title or "自动上传")
                logger.info("已在 contenteditable 区域填写文案。")
            except Exception:
                logger.debug("无法自动填充文案，请手动填写或提供更精确 selector。")

        human_sleep(0.8, 1.5)

        # 尝试点击发布按钮（多种后备 selector）
        publish_selectors = [
            (By.XPATH, "//button[contains(., '发布')]"),
            (By.XPATH, "//button[contains(., '提交')]"),
            (By.CSS_SELECTOR, "button.publish, button.btn-publish"),
        ]
        for by, sel in publish_selectors:
            try:
                btn = self.driver.find_element(by, sel)
                btn.click()
                logger.info("点击发布按钮 (selector=%s)", sel)
                human_sleep(2.0, 5.0)
                return True
            except Exception:
                continue

        logger.warning("未能找到发布按钮，请在页面手动发布。")
        return False
