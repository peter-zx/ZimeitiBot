# -*- coding: utf-8 -*-
from core.browser import create_driver, stop_driver
from platforms.xiaohongshu import XiaoHongShu

def main():
    driver = create_driver(headless=False)
    xhs = XiaoHongShu(driver)
    xhs.login_scan()
    input("扫码后按 Enter 退出...")
    stop_driver(driver)

if __name__ == "__main__":
    main()
