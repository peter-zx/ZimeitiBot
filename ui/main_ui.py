# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget,
    QTextEdit, QLineEdit, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from ui.platform_config_dialog import PlatformConfigDialog
from utils.config_manager import load_platforms

class MainWindow(QWidget):
    def __init__(self, username="user"):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"自媒体助手 - {self.username}")
        self.resize(1200, 760)
        self.platforms = {}
        self._build()
        self._load_platforms()

    def _build(self):
        root = QHBoxLayout()
        # 左侧
        left_box = QGroupBox("平台管理 / 配置")
        left = QVBoxLayout()
        self.platform_list = QListWidget()
        left.addWidget(self.platform_list)
        ops = QHBoxLayout()
        self.btn_add = QPushButton("新增平台")
        self.btn_edit = QPushButton("编辑平台")
        self.btn_del = QPushButton("删除平台")
        ops.addWidget(self.btn_add); ops.addWidget(self.btn_edit); ops.addWidget(self.btn_del)
        left.addLayout(ops)
        left.addWidget(QLabel("配置摘要："))
        self.platform_summary = QTextEdit(); self.platform_summary.setReadOnly(True)
        left.addWidget(self.platform_summary)
        left_box.setLayout(left); left_box.setMaximumWidth(420)

        # 中间（任务区 占位）
        mid_box = QGroupBox("任务区（占位）")
        mid = QVBoxLayout()
        self.search_box = QLineEdit(); self.search_box.setPlaceholderText("搜索任务（占位）")
        mid.addWidget(self.search_box)
        self.task_list = QListWidget()
        mid.addWidget(self.task_list)
        mid_box.setLayout(mid)

        # 右侧（执行区 占位）
        right_box = QGroupBox("执行区（占位）")
        right = QVBoxLayout()
        self.btn_run_sel = QPushButton("运行选中任务（占位）")
        self.btn_run_all = QPushButton("运行全部任务（占位）")
        right.addWidget(self.btn_run_sel); right.addWidget(self.btn_run_all)
        right.addWidget(QLabel("运行日志："))
        self.log_view = QTextEdit(); self.log_view.setReadOnly(True)
        right.addWidget(self.log_view)
        right_box.setLayout(right); right_box.setMaximumWidth(420)

        root.addWidget(left_box, 4)
        root.addWidget(mid_box, 4)
        root.addWidget(right_box, 3)
        self.setLayout(root)

        # 事件
        self.platform_list.itemSelectionChanged.connect(self._refresh_summary)
        self.btn_add.clicked.connect(self._on_add_platform)
        self.btn_edit.clicked.connect(self._on_edit_platform)
        self.btn_del.clicked.connect(self._on_delete_platform)

        # 占位
        self.btn_run_sel.clicked.connect(lambda: self.log_view.append("运行选中任务（占位）"))
        self.btn_run_all.clicked.connect(lambda: self.log_view.append("运行全部任务（占位）"))

    def _load_platforms(self):
        self.platforms = load_platforms()
        self.platform_list.clear()
        for name in self.platforms.keys():
            self.platform_list.addItem(name)
        if self.platform_list.count() > 0:
            self.platform_list.setCurrentRow(0)
        self._refresh_summary()

    def _refresh_summary(self):
        it = self.platform_list.currentItem()
        if not it:
            self.platform_summary.clear(); return
        name = it.text()
        cfg = self.platforms.get(name, {})
        lines = [
            f"平台：{name}",
            f"登录URL：{cfg.get('login_url','')}",
            f"编辑器URL：{cfg.get('editor_url','')}",
            f"上传选择器：{cfg.get('upload_selector','')}",
            "",
            "备注：",
            cfg.get('notes',''),
            "",
            "步骤："
        ]
        for idx, s in enumerate(cfg.get("steps", []), 1):
            action = s.get("action","")
            tpl = s.get("template_path","")
            sel = s.get("selector","")
            fill = s.get("fill_from","")
            lines.append(f"{idx}. {s.get('step_name','(未命名)')}  [{action}]")
            if tpl: lines.append(f"    模板：{tpl}")
            if sel: lines.append(f"    选择器：{sel}")
            if fill: lines.append(f"    输入来源：{fill}")
        self.platform_summary.setPlainText("\n".join(lines))

    def _on_add_platform(self):
        dlg = PlatformConfigDialog(parent=self)
        if dlg.exec_():
            self._load_platforms()

    def _on_edit_platform(self):
        it = self.platform_list.currentItem()
        if not it:
            return
        name = it.text()
        cfg = self.platforms.get(name, {})
        dlg = PlatformConfigDialog(name=name, initial=cfg, parent=self)
        if dlg.exec_():
            self._load_platforms()

    def _on_delete_platform(self):
        it = self.platform_list.currentItem()
        if not it:
            return
        name = it.text()
        from utils.config_manager import delete_platform
        from PyQt5.QtWidgets import QMessageBox as QM
        if QM.question(self, "确认", f"删除平台 [{name}] 及其模板？", QM.Yes|QM.No, QM.No) == QM.Yes:
            delete_platform(name)
            self._load_platforms()
