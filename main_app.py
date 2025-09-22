# -*- coding: utf-8 -*-
<<<<<<< HEAD
import sys
from PyQt6.QtWidgets import QApplication
from ui.startup_ui import StartupWindow

def main():
    app = QApplication(sys.argv)
    window = StartupWindow()
    window.show()
    sys.exit(app.exec())
=======
"""
main_app.py — 自媒体自动助手（管理员管理 + 程序内任务管理 + 提醒）
覆盖保存到项目根，运行: python main_app.py

说明：
- 用户/密码保存在 config/users.json（使用 PBKDF2-SHA256 哈希 + salt）
- 任务保存在 tasks/tasks.json（可通过 UI 新建/编辑/删除）
- 通知使用 plyer.notification（若未安装，退回弹窗）
- upload/publish 逻辑通过 core.uploader.Uploader 调用（若实现会执行）
"""

import sys
import os
import json
import threading
import queue
import time
import hashlib
import binascii
from pathlib import Path
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFormLayout, QSpinBox, QDateTimeEdit, QCheckBox, QGroupBox
)
from PyQt5.QtCore import QTimer, Qt

# optional notification lib
try:
    from plyer import notification as plyer_notify
except Exception:
    plyer_notify = None

# uploader (视觉+Selenium) - optional
try:
    from core.uploader import Uploader
except Exception:
    Uploader = None

ROOT = Path(os.getcwd())
CONFIG_DIR = ROOT / "config"
USERS_JSON = CONFIG_DIR / "users.json"
TEMPLATES_JSON = CONFIG_DIR / "templates.json"
TASKS_JSON = ROOT / "tasks" / "tasks.json"
TASKS_DIR = ROOT / "tasks"
TEMPLATES_DIR = CONFIG_DIR / "templates"

# ensure dirs
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
TASKS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# thread-safe log queue
log_q = queue.Queue()

# -------------------- helpers --------------------
def push_log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_q.put(f"[{ts}] {msg}")

def load_json(p: Path, default=None):
    if default is None:
        default = {}
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# -------------------- password hashing --------------------
def hash_password(password: str, salt: bytes = None):
    """
    返回 hex 格式: salt_hex$hash_hex
    使用 PBKDF2-HMAC-SHA256
    """
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000)
    return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def verify_password(stored: str, password: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split('$')
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000)
        return binascii.hexlify(dk).decode() == hash_hex
    except Exception:
        return False

# -------------------- user management --------------------
def ensure_default_admin():
    users = load_json(USERS_JSON, default={})
    if not users:
        users = {"admin": {"password": hash_password("admin"), "role": "admin"}}
        save_json(USERS_JSON, users)
        push_log("默认管理员 admin 已创建（密码 admin），请登录后修改密码。")
    return users

def add_user(username: str, password: str, role: str = "user"):
    users = load_json(USERS_JSON, default={})
    if username in users:
        raise ValueError("用户已存在")
    users[username] = {"password": hash_password(password), "role": role}
    save_json(USERS_JSON, users)
    push_log(f"新增用户: {username}")

def delete_user(username: str):
    users = load_json(USERS_JSON, default={})
    if username in users:
        del users[username]
        save_json(USERS_JSON, users)
        push_log(f"删除用户: {username}")
    else:
        raise ValueError("用户不存在")

def change_password(username: str, new_password: str):
    users = load_json(USERS_JSON, default={})
    if username not in users:
        raise ValueError("用户不存在")
    users[username]["password"] = hash_password(new_password)
    save_json(USERS_JSON, users)
    push_log(f"用户 {username} 密码已更新")

# -------------------- tasks persistence --------------------
def load_tasks():
    data = load_json(TASKS_JSON, default=[])
    return data

def save_tasks(tasks):
    save_json(TASKS_JSON, tasks)

# -------------------- notification --------------------
def notify_short(title: str, message: str):
    if plyer_notify:
        try:
            plyer_notify.notify(title=title, message=message, timeout=8)
            return
        except Exception:
            pass
    # fallback
    QMessageBox.information(None, title, message)

# -------------------- Login Dialog --------------------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录 - 自媒体助手")
        self.resize(380, 160)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("用户名:", self.username)
        form.addRow("密码:", self.password)
        layout.addLayout(form)

        h = QHBoxLayout()
        btn_login = QPushButton("登录")
        btn_login.clicked.connect(self.on_login)
        btn_register = QPushButton("创建管理员（如果不存在）")
        btn_register.clicked.connect(self.ensure_admin)
        h.addWidget(btn_login)
        h.addWidget(btn_register)
        layout.addLayout(h)

        self.setLayout(layout)
        ensure_default_admin()
        self.current_user = None

    def ensure_admin(self):
        users = load_json(USERS_JSON, default={})
        if "admin" in users:
            QMessageBox.information(self, "提示", "管理员已存在。")
        else:
            add_user("admin", "admin", "admin")
            QMessageBox.information(self, "已创建", "管理员已创建：用户名=admin 密码=admin")

    def on_login(self):
        users = load_json(USERS_JSON, default={})
        u = self.username.text().strip()
        p = self.password.text()
        if u in users and verify_password(users[u]["password"], p):
            push_log(f"用户 {u} 登录成功")
            self.current_user = u
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

# -------------------- Admin Management Dialog --------------------
class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理员管理")
        self.resize(520, 380)
        layout = QVBoxLayout()

        self.user_list = QListWidget()
        layout.addWidget(QLabel("用户列表："))
        layout.addWidget(self.user_list)

        form = QFormLayout()
        self.new_username = QLineEdit()
        self.new_password = QLineEdit()
        form.addRow("新用户名:", self.new_username)
        form.addRow("密码:", self.new_password)
        layout.addLayout(form)

        h = QHBoxLayout()
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self.on_add)
        del_btn = QPushButton("删除选中用户")
        del_btn.clicked.connect(self.on_delete)
        chpwd_btn = QPushButton("修改选中用户密码")
        chpwd_btn.clicked.connect(self.on_change_password)
        h.addWidget(add_btn); h.addWidget(del_btn); h.addWidget(chpwd_btn)
        layout.addLayout(h)

        self.setLayout(layout)
        self.refresh_users()

    def refresh_users(self):
        self.user_list.clear()
        users = load_json(USERS_JSON, default={})
        for u,meta in users.items():
            self.user_list.addItem(f"{u}  ({meta.get('role','')})")

    def on_add(self):
        u = self.new_username.text().strip()
        p = self.new_password.text()
        if not u or not p:
            QMessageBox.warning(self, "错误", "用户名/密码不能为空")
            return
        try:
            add_user(u, p, role="user")
            self.refresh_users()
            QMessageBox.information(self, "成功", f"新增用户 {u}")
            self.new_username.clear(); self.new_password.clear()
        except Exception as e:
            QMessageBox.warning(self, "失败", str(e))

    def on_delete(self):
        item = self.user_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选中用户")
            return
        uname = item.text().split()[0]
        if uname == "admin":
            QMessageBox.warning(self, "禁止", "不能删除默认 admin")
            return
        try:
            delete_user(uname)
            self.refresh_users()
            QMessageBox.information(self, "已删除", f"用户 {uname} 已删除")
        except Exception as e:
            QMessageBox.warning(self, "失败", str(e))

    def on_change_password(self):
        item = self.user_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选中用户")
            return
        uname = item.text().split()[0]
        newpwd, ok = QInputDialog.getText(self, "修改密码", f"为用户 {uname} 输入新密码：", QLineEdit.Password)
        if ok and newpwd:
            try:
                change_password(uname, newpwd)
                QMessageBox.information(self, "成功", "密码已修改")
            except Exception as e:
                QMessageBox.warning(self, "失败", str(e))

# -------------------- Main Window --------------------
class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle(f"自媒体自动助手 - 已登录: {self.current_user}")
        self.resize(1200, 720)
        self.templates = load_json(TEMPLATES_JSON, default={})
        self.tasks = load_tasks()
        self.uploader_cls = Uploader  # optional
        self.init_ui()
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.flush_logs)
        self.log_timer.start(300)
        self.scheduler_timer = QTimer()
        self.scheduler_timer.setInterval(5000)
        self.scheduler_timer.timeout.connect(self.check_and_run_due_tasks)
        self.scheduler_timer.start()

    def init_ui(self):
        central = QWidget()
        h = QHBoxLayout()

        # left config
        left = QVBoxLayout()
        left.addWidget(QLabel("<b>配置区</b>"))

        self.platform_selector = QComboBox()
        self.platform_selector.addItems(["小红书"])
        left.addWidget(QLabel("平台："))
        left.addWidget(self.platform_selector)

        form = QFormLayout()
        self.login_url = QLineEdit(self.templates.get("login_url", "https://creator.xiaohongshu.com/login"))
        form.addRow("登录 URL:", self.login_url)
        self.chromedriver = QLineEdit(self.templates.get("chromedriver", str(ROOT / "chromedriver-win64" / "chromedriver.exe")))
        form.addRow("Chromedriver:", self.chromedriver)
        left.addLayout(form)

        btn_pub = QPushButton("发布按钮（设置模板）")
        btn_pub.clicked.connect(lambda: self.choose_template("publish_button"))
        left.addWidget(btn_pub)
        self.pub_label = QLabel(self.templates.get("publish_button", "未设置"))
        left.addWidget(self.pub_label)

        btn_up = QPushButton("上传图文（设置模板）")
        btn_up.clicked.connect(lambda: self.choose_template("upload_image_button"))
        left.addWidget(btn_up)
        self.up_label = QLabel(self.templates.get("upload_image_button", "未设置"))
        left.addWidget(self.up_label)

        btn_sub = QPushButton("发布确认（设置模板）")
        btn_sub.clicked.connect(lambda: self.choose_template("submit_button"))
        left.addWidget(btn_sub)
        self.sub_label = QLabel(self.templates.get("submit_button", "未设置"))
        left.addWidget(self.sub_label)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_templates)
        left.addWidget(save_btn)

        # admin management only for admins
        users = load_json(USERS_JSON, default={})
        if users.get(self.current_user, {}).get("role") == "admin":
            admin_btn = QPushButton("管理员管理")
            admin_btn.clicked.connect(self.open_admin_manager)
            left.addWidget(admin_btn)

        left.addStretch()
        left_box = QGroupBox("配置区")
        left_box.setLayout(left)
        left_box.setMaximumWidth(360)

        # middle - tasks
        mid = QVBoxLayout()
        mid.addWidget(QLabel("<b>任务设置（在此新建/编辑/删除）</b>"))

        form_task = QFormLayout()
        self.task_image = QLineEdit()
        btn_choose = QPushButton("选择素材")
        btn_choose.clicked.connect(self.choose_task_image)
        h1 = QHBoxLayout(); h1.addWidget(self.task_image); h1.addWidget(btn_choose)
        form_task.addRow("素材路径:", h1)

        self.task_title = QLineEdit()
        form_task.addRow("标题:", self.task_title)
        self.task_content = QLineEdit()
        form_task.addRow("正文/简介:", self.task_content)

        self.immediate_chk = QCheckBox("立即执行（勾选则忽略发布时间）")
        form_task.addRow(self.immediate_chk)

        self.task_time = QDateTimeEdit()
        self.task_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.task_time.setCalendarPopup(True)
        form_task.addRow("发布时间:", self.task_time)

        self.remind_spin = QSpinBox()
        self.remind_spin.setRange(0, 1440)
        self.remind_spin.setValue(0)
        form_task.addRow("提前提醒（分钟）:", self.remind_spin)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 20)
        self.retry_spin.setValue(0)
        form_task.addRow("失败重试次数:", self.retry_spin)

        btn_add = QPushButton("添加任务")
        btn_add.clicked.connect(self.add_task)
        btn_del = QPushButton("删除选中任务")
        btn_del.clicked.connect(self.delete_selected_task)
        form_task.addRow(btn_add, btn_del)

        mid.addLayout(form_task)
        mid.addWidget(QLabel("任务列表（双击可编辑）"))
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        mid.addWidget(self.task_list)

        btn_save_tasks = QPushButton("保存任务到磁盘")
        btn_save_tasks.clicked.connect(self.save_tasks_ui)
        mid.addWidget(btn_save_tasks)
        mid_box = QGroupBox("任务区")
        mid_box.setLayout(mid)

        # right - run & logs
        right = QVBoxLayout()
        right.addWidget(QLabel("<b>执行区</b>"))
        btn_run_sel = QPushButton("运行选中任务")
        btn_run_all = QPushButton("运行所有任务")
        btn_run_sel.clicked.connect(self.run_selected)
        btn_run_all.clicked.connect(self.run_all)
        right.addWidget(btn_run_sel)
        right.addWidget(btn_run_all)

        self.log_text = QTextEdit(); self.log_text.setReadOnly(True)
        right.addWidget(QLabel("日志"))
        right.addWidget(self.log_text)

        right_box = QGroupBox("执行/日志")
        right_box.setLayout(right)
        right_box.setMaximumWidth(420)

        # assemble
        h.addWidget(left_box)
        h.addWidget(mid_box)
        h.addWidget(right_box)
        central.setLayout(h)
        self.setCentralWidget(central)
        self.refresh_templates_ui()
        self.refresh_task_list()

    # ---------- templates ----------
    def choose_template(self, key):
        fn, _ = QFileDialog.getOpenFileName(self, "选择模板图片", str(ROOT), "Images (*.png *.jpg *.bmp)")
        if not fn:
            return
        import shutil
        dst = TEMPLATES_DIR / Path(fn).name
        shutil.copy(fn, dst)
        self.templates[key] = str(dst)
        push_log(f"模板 {key} 已保存: {dst}")
        self.refresh_templates_ui()

    def refresh_templates_ui(self):
        self.pub_label.setText(self.templates.get("publish_button", "未设置"))
        self.up_label.setText(self.templates.get("upload_image_button", "未设置"))
        self.sub_label.setText(self.templates.get("submit_button", "未设置"))
        self.chromedriver.setText(self.templates.get("chromedriver", self.chromedriver.text()))

    def save_templates(self):
        self.templates["chromedriver"] = self.chromedriver.text().strip()
        self.templates["login_url"] = self.login_url.text().strip()
        save_json(TEMPLATES_JSON, self.templates)
        push_log("模板配置已保存")

    # ---------- admin ----------
    def open_admin_manager(self):
        dlg = AdminDialog(self)
        dlg.exec_()

    # ---------- tasks ----------
    def add_task(self):
        img = self.task_image.text().strip()
        if not img:
            QMessageBox.warning(self, "错误", "请选择素材文件")
            return
        if not os.path.isabs(img):
            img = str((TASKS_DIR / img).resolve())
        title = self.task_title.text().strip()
        content = self.task_content.text().strip()
        immediate = self.immediate_chk.isChecked()
        time_str = None
        if not immediate:
            time_str = self.task_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        remind_minutes = int(self.remind_spin.value())
        retries = int(self.retry_spin.value())
        task = {
            "platform": self.platform_selector.currentText(),
            "image": img,
            "title": title,
            "content": content,
            "time": time_str,
            "remind_minutes": remind_minutes,
            "retries": retries,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "reminded": False
        }
        self.tasks.append(task)
        self.save_and_refresh_tasks()
        push_log(f"添加任务: {img}")

    def delete_selected_task(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选中任务")
            return
        idx = self.task_list.row(item)
        self.tasks.pop(idx)
        self.save_and_refresh_tasks()
        push_log(f"已删除任务 #{idx}")

    def refresh_task_list(self):
        self.task_list.clear()
        for t in self.tasks:
            time_str = t.get("time") or "立即"
            item = QListWidgetItem(f"[{t.get('platform')}] {Path(t.get('image')).name} | {t.get('title')} | {time_str}")
            self.task_list.addItem(item)

    def save_and_refresh_tasks(self):
        save_tasks(self.tasks)
        self.refresh_task_list()

    def save_tasks_ui(self):
        save_tasks(self.tasks)
        push_log("任务已保存到 disk")

    def choose_task_image(self):
        fn, _ = QFileDialog.getOpenFileName(self, "选择素材", str(TASKS_DIR), "Images/Videos (*.png *.jpg *.jpeg *.mp4 *.mov)")
        if fn:
            self.task_image.setText(fn)

    def edit_task(self, item: QListWidgetItem):
        idx = self.task_list.row(item)
        t = self.tasks[idx]
        dlg = QDialog(self)
        dlg.setWindowTitle("编辑任务")
        layout = QVBoxLayout()
        form = QFormLayout()
        img_e = QLineEdit(t.get("image",""))
        btn_pick = QPushButton("选择素材")
        btn_pick.clicked.connect(lambda: img_e.setText(QFileDialog.getOpenFileName(self,"选择素材",str(TASKS_DIR),"Images/Videos (*.png *.jpg *.jpeg *.mp4 *.mov)")[0]))
        form.addRow("素材:", img_e)
        title_e = QLineEdit(t.get("title",""))
        form.addRow("标题:", title_e)
        content_e = QLineEdit(t.get("content",""))
        form.addRow("正文:", content_e)
        immediate_chk = QCheckBox("立即执行")
        if not t.get("time"):
            immediate_chk.setChecked(True)
        time_e = QDateTimeEdit()
        time_e.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        try:
            if t.get("time"):
                dt = datetime.fromisoformat(t.get("time"))
                time_e.setDateTime(dt)
        except Exception:
            pass
        form.addRow("发布时间:", time_e)
        remind_e = QSpinBox(); remind_e.setRange(0,1440); remind_e.setValue(t.get("remind_minutes",0))
        form.addRow("提前提醒(min):", remind_e)
        layout.addLayout(form)
        h = QHBoxLayout()
        ok = QPushButton("保存"); cancel = QPushButton("取消")
        ok.clicked.connect(lambda: self._save_edited_task(idx, img_e.text(), title_e.text(), content_e.text(), time_e, immediate_chk.isChecked(), remind_e.value(), dlg))
        cancel.clicked.connect(dlg.reject)
        h.addWidget(ok); h.addWidget(cancel)
        layout.addLayout(h)
        dlg.setLayout(layout)
        dlg.exec_()

    def _save_edited_task(self, idx, image, title, content, time_widget, immediate, remind_minutes, dlg):
        t = self.tasks[idx]
        t["image"] = image
        t["title"] = title
        t["content"] = content
        t["remind_minutes"] = remind_minutes
        t["time"] = None if immediate else time_widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        save_tasks(self.tasks)
        self.refresh_task_list()
        dlg.accept()
        push_log(f"任务 #{idx} 已更新")

    # ---------- execution ----------
    def run_selected(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选中一项")
            return
        idx = self.task_list.row(item)
        t = threading.Thread(target=self.worker_run_task, args=(idx,), daemon=True)
        t.start()
        push_log(f"开始执行任务 #{idx}")

    def run_all(self):
        t = threading.Thread(target=self.worker_run_all, daemon=True)
        t.start()
        push_log("开始执行全部任务（后台）")

    def worker_run_all(self):
        for i in range(len(self.tasks)):
            self.worker_run_task(i)
            time.sleep(2)
        push_log("全部任务执行完毕")

    def worker_run_task(self, idx):
        try:
            task = self.tasks[idx]
        except IndexError:
            return
        push_log(f"执行任务 #{idx}: {task.get('image')}")
        # call core.uploader if present
        if self.uploader_cls is None:
            push_log("Uploader 未实现，当前为模拟执行（在实现 uploader 后可自动化）")
            time.sleep(2)
            task["status"] = "done"
            self.save_and_refresh_tasks()
            return

        u = self.uploader_cls(debug=False)
        # visual open editor
        pub_tpl = self.templates.get("publish_button")
        up_tpl = self.templates.get("upload_image_button")
        sub_tpl = self.templates.get("submit_button")
        chromedrv = self.templates.get("chromedriver", str(ROOT / "chromedriver-win64" / "chromedriver.exe"))
        if pub_tpl:
            push_log("视觉尝试点击发布入口...")
            ok = u.click_button(pub_tpl, confidence=0.8)
            if not ok:
                push_log("视觉点击失败，继续尝试 Selenium 上传")
        if up_tpl:
            push_log("视觉尝试点击上传图文...")
            ok = u.click_button(up_tpl, confidence=0.8)
            if not ok:
                push_log("视觉点击上传失败，继续尝试 Selenium 上传")
        # selenium upload & fill
        driver = u.upload_image_via_selenium_with_fill(
            chromedriver_path=chromedrv,
            file_path=task.get("image"),
            title_text=task.get("title",""),
            content_text=task.get("content",""),
            editor_url=self.templates.get("login_url", "https://creator.xiaohongshu.com/create"),
            input_selector="//input[@type='file']",
            title_selector="//input[@id='title' or @name='title']",
            content_selector="//textarea"
        )
        if not driver:
            push_log("Selenium 上传失败")
            task["status"] = "error"
            self.save_and_refresh_tasks()
            return
        time.sleep(1)
        # try visual submit
        if sub_tpl:
            ok = u.click_button(sub_tpl, confidence=0.8)
            if ok:
                push_log("视觉点击发布成功")
                task["status"] = "done"
                self.save_and_refresh_tasks()
                try:
                    driver.quit()
                except:
                    pass
                return
        # fallback to selenium click
        try:
            from selenium.webdriver.common.by import By
            btn = driver.find_element(By.XPATH, "//button[contains(., '发布') or contains(., '提交')]")
            btn.click()
            push_log("Selenium 点击发布按钮")
            task["status"] = "done"
        except Exception as e:
            push_log(f"Selenium 点击失败: {e}")
            task["status"] = "error"
        finally:
            try:
                driver.quit()
            except:
                pass
        self.save_and_refresh_tasks()

    # ---------- scheduler (reminders + due tasks) ----------
    def check_and_run_due_tasks(self):
        now = datetime.now()
        for idx, t in enumerate(self.tasks):
            # remind
            remind_m = int(t.get("remind_minutes", 0) or 0)
            if t.get("time") and remind_m > 0 and not t.get("reminded", False):
                try:
                    due_dt = datetime.fromisoformat(t["time"])
                except Exception:
                    try:
                        due_dt = datetime.strptime(t["time"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                remind_time = due_dt - timedelta(minutes=remind_m)
                if now >= remind_time and now < due_dt:
                    notify_short("任务提醒", f"任务即将到点：{Path(t.get('image')).name} 将在 {t['time']} 发布")
                    push_log(f"提醒已发送（任务 #{idx}）")
                    t["reminded"] = True
                    save_tasks(self.tasks)
            # due execution (自动执行)
            if t.get("time"):
                try:
                    due_dt = datetime.fromisoformat(t["time"])
                except Exception:
                    try:
                        due_dt = datetime.strptime(t["time"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        continue
                if due_dt <= now and t.get("status") != "done":
                    push_log(f"检测到到期任务 #{idx}，自动执行")
                    thr = threading.Thread(target=self.worker_run_task, args=(idx,), daemon=True)
                    thr.start()
                    self.worker_threads.append(thr)

    # ---------- logs ----------
    def flush_logs(self):
        while not log_q.empty():
            msg = log_q.get_nowait()
            self.log_text.append(msg)

# -------------------- entry point --------------------
def main():
    ensure_default_admin()
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() != QDialog.Accepted:
        print("取消登录，退出")
        return
    current_user = login.current_user
    w = MainWindow(current_user)
    w.show()
    push_log("程序就绪")
    sys.exit(app.exec_())
>>>>>>> ce80e5302e41d8bd1ff7348442b2c7bac06778b6

if __name__ == "__main__":
    main()
