# -*- coding: utf-8 -*-
from core.uploader import Uploader
import time

def main():
    uploader = Uploader()

    # 点击左上角 发布笔记
    uploader.click_button(r"E:\ai_work\zimeitiboot\sucaixiaohongshu\publish_button.png")
    time.sleep(1)

    # 点击上传图文
    uploader.click_button(r"E:\ai_work\zimeitiboot\sucaixiaohongshu\upload_image_button.png")
    time.sleep(1)

    # 上传图片
    uploader.upload_image(r"E:\ai_work\zimeitiboot\ceshi\绘制插图 (13).png")
    print("上传流程执行完成")

if __name__ == "__main__":
    main()
