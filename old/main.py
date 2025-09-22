# main.py
from core.browser import create_driver
from core.file_handler import FileHandler
from core.uploader import Uploader
from platforms.xiaohongshu import XiaoHongShu
from utils.logger import get_logger
import time

logger = get_logger("main")

def main():
    print("启动自媒体自动化助手（MVP）")
    driver = create_driver(headless=False)
    xhs = XiaoHongShu(driver)

    # 打开登录页并手动登录
    xhs.open_login_page()
    input("请在浏览器中完成登录（扫码或手动），登录完成后按 Enter 继续...")

    # 尝试导航到编辑器
    print("尝试自动打开/导航到发布编辑器（若失败请手动在浏览器打开编辑器页）")
    xhs.navigate_to_create_editor()
    time.sleep(1)

    # 选择文件夹（在登录后）
    fh = FileHandler()
    folder = fh.select_folder_dialog(initialdir=".")
    if not folder:
        print("未选择文件夹，退出。")
        driver.quit()
        return
    files = fh.load_files_from_folder()
    print(f"已加载 {len(files)} 个文件。")

    # 批量上传
    uploader = Uploader(driver)
    results = uploader.batch_upload_folder(folder)
    print("上传结果：", results)

    input("所有任务完成，按 Enter 关闭浏览器并退出...")
    driver.quit()

if __name__ == "__main__":
    main()
