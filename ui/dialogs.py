# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QTextEdit, QListWidget, QListWidgetItem, QFormLayout
)
from PyQt6.QtCore import Qt
from utils.config_manager import add_or_update_platform, list_templates, add_template

class PlatformConfigDialog(QDialog):
    """
    添加 / 编辑 平台配置对话框
    fields: name, login_url, editor_url, upload_selector, notes
    点击【保存】会把配置信息写入 config/platforms.json（通过 utils.config_manager）
    """
    def __init__(self, name=None, initial_config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("平台配置" + (f" — 编辑 {name}" if name else " — 新建"))
        self.resize(620, 420)
        self.platform_name = name or ""
        self.initial = initial_config or {}
        self._build()
        if self.initial:
            self._load_initial(self.initial)

    def _build(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_edit = QLineEdit(self.platform_name)
        self.login_url_edit = QLineEdit()
        self.editor_url_edit = QLineEdit()
        self.upload_selector_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)

        form.addRow("平台名称:", self.name_edit)
        form.addRow("登录 URL:", self.login_url_edit)
        form.addRow("编辑器 URL:", self.editor_url_edit)
        form.addRow("上传选择器 (XPath/CSS):", self.upload_selector_edit)
        layout.addLayout(form)
        layout.addWidget(QLabel("备注 / 指导说明（可写操作步骤或注意事项）:"))
        layout.addWidget(self.notes_edit)

        # template manager
        tpl_h = QHBoxLayout()
        self.tpl_list = QListWidget()
        tpl_h.addWidget(self.tpl_list)
        tpl_ops_v = QVBoxLayout()
        self.add_tpl_btn = QPushButton("添加模板图片")
        self.add_tpl_btn.clicked.connect(self.on_add_template)
        self.remove_tpl_btn = QPushButton("删除所选模板")
        self.remove_tpl_btn.clicked.connect(self.on_remove_template)
        tpl_ops_v.addWidget(self.add_tpl_btn)
        tpl_ops_v.addWidget(self.remove_tpl_btn)
        tpl_ops_v.addStretch()
        tpl_h.addLayout(tpl_ops_v)
        layout.addWidget(QLabel("模板图片（用于视觉匹配）:"))
        layout.addLayout(tpl_h)

        btn_h = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_h.addStretch()
        btn_h.addWidget(self.save_btn)
        btn_h.addWidget(self.cancel_btn)
        layout.addLayout(btn_h)

        self.setLayout(layout)

    def _load_initial(self, cfg: dict):
        self.name_edit.setText(cfg.get("name", self.platform_name))
        self.login_url_edit.setText(cfg.get("login_url", ""))
        self.editor_url_edit.setText(cfg.get("editor_url", ""))
        self.upload_selector_edit.setText(cfg.get("upload_selector", ""))
        self.notes_edit.setPlainText(cfg.get("notes", ""))
        # load templates
        self._refresh_templates()

    def _refresh_templates(self):
        self.tpl_list.clear()
        name = self.name_edit.text().strip()
        if not name:
            return
        for p in list_templates(name):
            item = QListWidgetItem(p)
            self.tpl_list.addItem(item)

    def on_add_template(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先填写平台名称（用于保存模板）")
            return
        fn, _ = QFileDialog.getOpenFileName(self, "选择模板图片", "", "Images (*.png *.jpg *.bmp)")
        if not fn:
            return
        try:
            dst = add_template(name, fn)
            QMessageBox.information(self, "已添加", f"模板已保存：{dst}")
            self._refresh_templates()
        except Exception as e:
            QMessageBox.warning(self, "失败", f"添加模板失败：{e}")

    def on_remove_template(self):
        it = self.tpl_list.currentItem()
        if not it:
            QMessageBox.information(self, "提示", "先选择一项模板")
            return
        p = it.text()
        # remove file
        import os
        try:
            os.remove(p)
            self._refresh_templates()
            QMessageBox.information(self, "已删除", "模板文件已删除")
        except Exception as e:
            QMessageBox.warning(self, "删除失败", str(e))

    def on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "平台名称不能为空")
            return
        cfg = {
            "name": name,
            "login_url": self.login_url_edit.text().strip(),
            "editor_url": self.editor_url_edit.text().strip(),
            "upload_selector": self.upload_selector_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip()
        }
        add_or_update_platform(name, cfg)
        QMessageBox.information(self, "已保存", f"平台 {name} 配置已保存")
        self.accept()
