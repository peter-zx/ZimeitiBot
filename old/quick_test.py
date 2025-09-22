# quick_test.py
from core.browser import create_driver
from core.file_handler import FileHandler
from platforms.xiaohongshu import XiaoHongShu
from core.uploader import Uploader, init_db, record_upload
from utils.logger import get_logger

logger = get_logger("quick_test")

def main():
    print("=== quick_test 开始 ===")
    driver = create_driver(headless=False)
    xhs = XiaoHongShu(driver)

    xhs.open_login_page()
    input("在浏览器完成登录后回到此处按 Enter 继续...")

    print("尝试自动进入编辑器（若失败，请在浏览器手动打开编辑器页面）。")
    xhs.navigate_to_create_editor()

    fh = FileHandler()
    folder = fh.select_folder_dialog(initialdir=".")
    if not folder:
        print("未选择文件夹，退出。")
        driver.quit()
        return
    files = fh.load_files_from_folder()
    if not files:
        print("未在文件夹中发现支持的媒体文件。")
        driver.quit()
        return

    init_db()
    uploader = Uploader(driver)
    first = files[0]
    ok = uploader.platform.upload_one_file(first, caption="quick_test 自动上传", title="")
    if ok:
        record_upload(first, "xiaohongshu", "success", "quick_test uploaded")
        print("上传成功（函数返回 True）。")
    else:
        record_upload(first, "xiaohongshu", "failed", "quick_test returned False")
        print("上传未返回成功（请检查页面或 selector）。")

    input("测试完成，按 Enter 关闭浏览器...")
    driver.quit()

if __name__ == "__main__":
    main()
