import os

# 项目根目录
root = r"E:\ai_work\zimeitiboot"

# 文件夹结构
folders = [
    "config",
    "core",
    "platforms",
    "ui",
    "tasks/images",
    "utils"
]

# 空文件列表
files = [
    "config/settings.py",
    "config/credentials.py",
    "core/browser.py",
    "core/uploader.py",
    "core/file_handler.py",
    "core/scheduler.py",
    "platforms/xiaohongshu.py",
    "ui/login_ui.py",
    "ui/main_ui.py",
    "ui/dialogs.py",
    "tasks/tasks.xlsx",
    "utils/logger.py",
    "utils/helpers.py",
    "main.py",
    "requirements.txt"
]

# 创建文件夹
for folder in folders:
    path = os.path.join(root, folder)
    os.makedirs(path, exist_ok=True)
    print(f"创建文件夹: {path}")

# 创建空文件
for file in files:
    path = os.path.join(root, file)
    with open(path, "w", encoding="utf-8") as f:
        pass
    print(f"创建空文件: {path}")

print("项目文件夹结构创建完成！")
