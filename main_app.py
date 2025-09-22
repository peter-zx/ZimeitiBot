# -*- coding: utf-8 -*-
"""
main_app.py
自媒体自动工具 — UI 原型
放在项目根后运行: python main_app.py
依赖: PyQt5, openpyxl
该原型会：
 - 管理平台模板（保存到 config/templates.json）
 - 导入任务 Excel（tasks/tasks.xlsx 或其他）
 - 在 UI 上选择任务并“立即执行”
 - 使用 core.uploader.Uploader 执行视觉点击与 Selenium 上传（若已实现）
 - 在日志窗口显示执行信息
"""

import sys
import os
import json
import threading
import queue
import time
from pathlib import Path

# GUI
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QCheckBox, QGroupBox, QFormLayout, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt

# Excel
try:
    import openpyxl
except Exception:
    openpyxl = None

# uploader (视觉+Selenium) - 我们调用已在 core/uploader.py 中实现的接口
try:
    from core.uploader import Uploader
except Exception:
    Uploader = None

# 项目根和配置路径
ROOT = Path(os.getcwd())
CONFIG_DIR = ROOT / "config"
TEMPLATES_JSON = CONFIG_DIR / "templates.json"
TASKS_DIR = ROOT / "tasks"
DEFAULT_TASKS_XLSX = TASKS_DIR / "tasks.xlsx"
CHROMEDRIVER_DEFAULT = str(ROOT / "chromedriver-win64" / "chromedriver.exe")

# 日志队列（线程安全）
log_q = queue.Queue()


# ---------------- helpers ----------------
def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)


def load_templates():
    ensure_dirs()
    if TEMPLATES_JSON.exists():
        try:
            return json.loads(TEMPLATES_JSON.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_templates(d: dict):
    ensure_dirs()
    TEMPLATES_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def push_log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    log_q.put(f"[{ts}] {msg}")


def read_tasks_from_excel(path):
    tasks = []
    if openpyxl is None:
        raise RuntimeError("openpyxl not installed")
    if not Path(path).exists():
        push_log(f"任务表不存在: {path}")
        return tasks
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        # image, title, content, publish_time
        if row[0] is None:
            continue
        img = str(row[0]).strip()
        title = str(row[1]).strip() if row[1] else ""
        content = str(row[2]).strip() if row[2] else ""
        pubtime = row[3]
        tasks.append({"image": img, "title": title, "content": content, "time": pubtime})
    return tasks


# ---------------- Login Dialog ----------------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录 - 自媒体自动助手")
        self.resize(360, 180)
        layout = QVBoxLayout()

        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("账号:", self.username)
        form.addRow("密码:", self.password)
        layout.addLayout(form)

        self.scan_btn = QPushButton("扫码/登录（Selenium 将打开浏览器以扫码）")
        self.scan_btn.clicked.connect(self.on_scan)
        layout.addWidget(self.scan_btn)

        self.login_btn = QPushButton("本地登录（占位，用于会员系统）")
        self.login_btn.clicked.connect(self.accept)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def on_scan(self):
        # 打开浏览器由 core.browser.create_driver + platforms.xiaohongshu.login_scan 执行
        QMessageBox.information(self, "提示", "扫码登录将在主界面触发（打开浏览器并扫码），请在主界面点击【打开登录】按钮。")


# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自媒体自动助手（原型）")
        self.resize(900, 700)
        ensure_dirs()
        self.templates = load_templates()
        self.tasks = []  # 列表 of dicts
        self.log_timer = QTimer()
        self.log_timer.setInterval(300)
        self.log_timer.timeout.connect(self.flush_logs)
        self.log_timer.start()

        self.worker_threads = []  # keep refs

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # Top: platform + chromedriver path + open login (Selenium)
        top_h = QHBoxLayout()
        top_h.addWidget(QLabel("平台:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["小红书"])  # 可扩展
        top_h.addWidget(self.platform_combo)

        top_h.addWidget(QLabel("Chromedriver:"))
        self.chromedriver_edit = QLineEdit(self.templates.get("chromedriver", CHROMEDRIVER_DEFAULT))
        top_h.addWidget(self.chromedriver_edit)
        self.chromedriver_btn = QPushButton("选择")
        self.chromedriver_btn.clicked.connect(self.choose_chromedriver)
        top_h.addWidget(self.chromedriver_btn)

        self.open_login_btn = QPushButton("打开平台登录(扫码)")
        self.open_login_btn.clicked.connect(self.open_platform_login)
        top_h.addWidget(self.open_login_btn)

        main_layout.addLayout(top_h)

        # Template group
        tpl_group = QGroupBox("平台模板（手动上传/替换按钮截图）")
        tpl_layout = QHBoxLayout()

        form_layout = QFormLayout()
        self.tpl_publish_edit = QLineEdit(self.templates.get("publish_button", ""))
        self.tpl_upload_edit = QLineEdit(self.templates.get("upload_image_button", ""))
        self.tpl_submit_edit = QLineEdit(self.templates.get("submit_button", ""))

        btn_pub = QPushButton("设置 发布按钮 图像")
        btn_pub.clicked.connect(lambda: self.choose_template("publish_button", self.tpl_publish_edit))
        btn_upload = QPushButton("设置 上传图文 图像")
        btn_upload.clicked.connect(lambda: self.choose_template("upload_image_button", self.tpl_upload_edit))
        btn_submit = QPushButton("设置 发布确认 图像")
        btn_submit.clicked.connect(lambda: self.choose_template("submit_button", self.tpl_submit_edit))

        form_layout.addRow(btn_pub, self.tpl_publish_edit)
        form_layout.addRow(btn_upload, self.tpl_upload_edit)
        form_layout.addRow(btn_submit, self.tpl_submit_edit)

        tpl_layout.addLayout(form_layout)
        save_tpl_btn = QPushButton("保存模板配置")
        save_tpl_btn.clicked.connect(self.save_template_config)
        tpl_layout.addWidget(save_tpl_btn)

        tpl_group.setLayout(tpl_layout)
        main_layout.addWidget(tpl_group)

        # Task manager: load Excel, table, run buttons
        task_group = QGroupBox("任务计划（Excel 导入）")
        task_layout = QVBoxLayout()

        task_btn_h = QHBoxLayout()
        self.load_tasks_btn = QPushButton("加载任务 Excel")
        self.load_tasks_btn.clicked.connect(self.load_tasks_dialog)
        task_btn_h.addWidget(self.load_tasks_btn)

        self.task_file_label = QLabel(str(DEFAULT_TASKS_XLSX))
        task_btn_h.addWidget(self.task_file_label)

        self.run_selected_btn = QPushButton("运行选中任务")
        self.run_selected_btn.clicked.connect(self.run_selected_task)
        task_btn_h.addWidget(self.run_selected_btn)

        self.run_all_btn = QPushButton("运行全部任务(按顺序)")
        self.run_all_btn.clicked.connect(self.run_all_tasks)
        task_btn_h.addWidget(self.run_all_btn)

        task_layout.addLayout(task_btn_h)

        # table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["图片路径", "标题", "正文", "发布时间"])
        self.table.setColumnWidth(0, 360)
        task_layout.addWidget(self.table)

        task_group.setLayout(task_layout)
        main_layout.addWidget(task_group, stretch=1)

        # Scheduler controls (placeholder)
        sched_group = QGroupBox("调度（占位）")
        sched_layout = QHBoxLayout()
        self.sched_enable = QCheckBox("启用调度（未来实现）")
        sched_layout.addWidget(self.sched_enable)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(60)
        sched_layout.addWidget(QLabel("轮询间隔(s):"))
        sched_layout.addWidget(self.interval_spin)
        sched_group.setLayout(sched_layout)
        main_layout.addWidget(sched_group)

        # Log viewer
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_btn)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, stretch=1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # load templates to edits
        self.refresh_template_edits()

    # ---------------- template handling ----------------
    def choose_template(self, key, line_edit: QLineEdit):
        fn, _ = QFileDialog.getOpenFileName(self, "选择模板图片", str(ROOT), "Image Files (*.png *.jpg *.bmp)")
        if not fn:
            return
        # copy to config/templates/ to keep consistent
        templates_dir = CONFIG_DIR / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        dst = templates_dir / Path(fn).name
        try:
            import shutil
            shutil.copy(fn, dst)
            line_edit.setText(str(dst))
            push_log(f"模板 {key} 保存为: {dst}")
        except Exception as e:
            push_log(f"复制模板失败: {e}")
            QMessageBox.warning(self, "错误", f"复制模板失败: {e}")

    def save_template_config(self):
        d = {
            "publish_button": self.tpl_publish_edit.text().strip(),
            "upload_image_button": self.tpl_upload_edit.text().strip(),
            "submit_button": self.tpl_submit_edit.text().strip(),
            "chromedriver": self.chromedriver_edit.text().strip()
        }
        save_templates(d)
        self.templates = d
        push_log("模板配置已保存")

    def refresh_template_edits(self):
        self.tpl_publish_edit.setText(self.templates.get("publish_button", ""))
        self.tpl_upload_edit.setText(self.templates.get("upload_image_button", ""))
        self.tpl_submit_edit.setText(self.templates.get("submit_button", ""))
        self.chromedriver_edit.setText(self.templates.get("chromedriver", CHROMEDRIVER_DEFAULT))

    def choose_chromedriver(self):
        fn, _ = QFileDialog.getOpenFileName(self, "选择 chromedriver", str(ROOT), "Executable Files (*)")
        if fn:
            self.chromedriver_edit.setText(fn)

    # ---------------- tasks ----------------
    def load_tasks_dialog(self):
        fn, _ = QFileDialog.getOpenFileName(self, "选择任务 Excel", str(TASKS_DIR), "Excel Files (*.xlsx *.xls)")
        if not fn:
            return
        self.task_file_label.setText(fn)
        self.load_tasks(fn)

    def load_tasks(self, excel_path=None):
        excel_path = excel_path or str(DEFAULT_TASKS_XLSX)
        try:
            tasks = read_tasks_from_excel(excel_path)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"读取任务失败: {e}")
            return
        self.tasks = tasks
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(0)
        for t in self.tasks:
            r = self.table.rowCount()
            self.table.insertRow(r)
            img_item = QTableWidgetItem(t["image"])
            title_item = QTableWidgetItem(t["title"])
            content_item = QTableWidgetItem(t["content"])
            time_item = QTableWidgetItem(str(t.get("time", "")))
            self.table.setItem(r, 0, img_item)
            self.table.setItem(r, 1, title_item)
            self.table.setItem(r, 2, content_item)
            self.table.setItem(r, 3, time_item)

    # ---------------- platform login ----------------
    def open_platform_login(self):
        # this will be a placeholder to trigger Selenium-based login
        push_log("打开平台登录（将由 core.browser + platforms.xiaohongshu 实现扫码）")
        QMessageBox.information(self, "登录提示", "请在浏览器中完成扫码登录（打开浏览器将由后台函数执行，暂为占位）")

    # ---------------- run tasks ----------------
    def run_selected_task(self):
        sel = self.table.currentRow()
        if sel < 0:
            QMessageBox.information(self, "提示", "请先选中一行任务")
            return
        task = self.tasks[sel]
        t = threading.Thread(target=self._worker_run_task, args=(task,), daemon=True)
        t.start()
        self.worker_threads.append(t)

    def run_all_tasks(self):
        if not self.tasks:
            QMessageBox.information(self, "提示", "任务列表为空")
            return
        t = threading.Thread(target=self._worker_run_all, daemon=True)
        t.start()
        self.worker_threads.append(t)

    # worker implementations
    def _worker_run_all(self):
        push_log("开始批量任务（按顺序）")
        for task in self.tasks:
            self._worker_run_task(task)
            # 人为间隔
            time.sleep(2)
        push_log("批量任务完成")

    def _worker_run_task(self, task: dict):
        # resolved paths
        img = task["image"]
        if not os.path.isabs(img):
            img = str(TASKS_DIR / img)
        title = task.get("title", "")
        content = task.get("content", "")
        push_log(f"执行任务: {img} | {title}")

        # instantiate uploader (calls core/uploader.Uploader)
        if Uploader is None:
            push_log("core.uploader.Uploader 未就绪，请确保 core/uploader.py 存在并可导入")
            return

        u = Uploader(debug=False)

        # Step 1: click publish button visually
        pub_tpl = self.tpl_publish_edit.text().strip()
        up_tpl = self.tpl_upload_edit.text().strip()
        sub_tpl = self.tpl_submit_edit.text().strip()
        chromedriver = self.chromedriver_edit.text().strip() or CHROMEDRIVER_DEFAULT

        if pub_tpl:
            push_log("视觉点击 发布按钮 ...")
            ok = u.click_button(pub_tpl, confidence=0.8)
            if not ok:
                push_log("未找到 发布 按钮（视觉），请检查模板或浏览器显示")
                # continue: allow attempts below
        else:
            push_log("未配置 publish_button 模板，跳过视觉点击")

        # try click upload button if configured
        if up_tpl:
            push_log("视觉点击 上传图文 按钮 ...")
            ok2 = u.click_button(up_tpl, confidence=0.8)
            if not ok2:
                push_log("未找到 上传图文 按钮（视觉），将尝试用 Selenium 打开编辑器并上传")
        else:
            push_log("未配置 upload_image_button 模板，继续用 Selenium 上传")

        # Use Selenium to upload the file and fill title/content
        push_log("启动 Selenium 上传并填写...")
        driver = u.upload_image_via_selenium_with_fill(
            chromedriver_path=chromedriver,
            file_path=img,
            title_text=title,
            content_text=content,
            editor_url=str(self.task_file_label.text()) if False else "https://creator.xiaohongshu.com/create",
            input_selector="//input[@type='file']",
            title_selector="//input[@id='title' or @name='title']",
            content_selector="//textarea"
        )
        if not driver:
            push_log("Selenium 上传或表单填写失败（函数返回 False）")
            return
        push_log("Selenium 已上传文件并尝试填写文案（可在浏览器手动确认发布）")

        # finally: try visual click submit, else selenium click
        time.sleep(1)
        if sub_tpl:
            push_log("视觉点击 发布确认 按钮 ...")
            ok3 = u.click_button(sub_tpl, confidence=0.8)
            if ok3:
                push_log("视觉点击发布成功")
                try:
                    driver.quit()
                except:
                    pass
                return
            else:
                push_log("视觉未找到发布确认，尝试 Selenium 点击")
        # selenium attempt
        try:
            from selenium.webdriver.common.by import By
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(., '发布') or contains(., '提交')]")
                btn.click()
                push_log("使用 Selenium 点击发布按钮")
            except Exception as e:
                push_log(f"Selenium 找不到发布按钮: {e}")
        finally:
            try:
                time.sleep(2)
                driver.quit()
            except:
                pass

        push_log("任务执行结束（请在平台上检查发布情况）")

    # ---------------- logs ----------------
    def flush_logs(self):
        while not log_q.empty():
            msg = log_q.get_nowait()
            self.log_text.append(msg)


# ---------------- main ----------------
def main():
    app = QApplication(sys.argv)

    login = LoginDialog()
    login.exec_()  # simple modal login (placeholder)

    w = MainWindow()
    w.show()
    push_log("程序就绪，打开界面。请配置模板并加载任务。")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
