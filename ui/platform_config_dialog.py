# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QListWidget,
    QListWidgetItem, QPushButton, QFileDialog, QMessageBox, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt
from utils.config_manager import add_or_update_platform, load_platforms, add_template_file, DEFAULT_STEPS

HELP_LOGIN = "登录URL：账号登录页地址（例如：创作平台的登录页面）。"
HELP_EDITOR = "编辑器URL：进入“发布/创建”的页面，如果没有固定URL，可留空，用步骤里的“点击发布入口（视觉）”实现。"
HELP_SELECTOR = "上传选择器：如果会写XPath/CSS，可填写 `<input type=file>` 的定位；不会就留空，用“点击上传按钮（视觉）”弹出文件框。"
HELP_FIND_SELECTOR = "如何查找：浏览器F12 → 选择元素 → 复制 XPath/CSS 选择器。"

ACTION_LIST = [
    ("click_template", "点击（视觉模板）"),
    ("type_template", "输入（视觉模板定位输入框）"),
    ("click_selector", "点击（DOM选择器）"),
    ("type_selector", "输入（DOM选择器定位输入框）")
]

FILL_FROM_LIST = ["", "task.title", "task.content"]

class PlatformConfigDialog(QDialog):
    def __init__(self, name:str="", initial:dict=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"平台配置 - {'编辑 ' + name if name else '新建'}")
        self.resize(820, 620)
        self.initial = initial or {}
        self._build()
        if name:
            self.name_edit.setText(name)
        if self.initial:
            self._load_initial(self.initial)

    def _build(self):
        layout = QVBoxLayout()

        # 基本配置
        basic = QFormLayout()
        self.name_edit = QLineEdit()
        self.login_url_edit = QLineEdit()
        self.editor_url_edit = QLineEdit()
        self.upload_selector_edit = QLineEdit()
        self.notes_edit = QTextEdit(); self.notes_edit.setFixedHeight(70)

        basic.addRow("平台名称：", self.name_edit)
        row_login = QHBoxLayout()
        row_login.addWidget(self.login_url_edit, 1)
        hl = QLabel(f"❓ {HELP_LOGIN}")
        hl.setStyleSheet("color:#666")
        row_login.addWidget(hl)
        basic.addRow("登录 URL：", row_login)

        row_editor = QHBoxLayout()
        row_editor.addWidget(self.editor_url_edit, 1)
        he = QLabel(f"❓ {HELP_EDITOR}")
        he.setStyleSheet("color:#666")
        row_editor.addWidget(he)
        basic.addRow("编辑器 URL：", row_editor)

        row_sel = QHBoxLayout()
        row_sel.addWidget(self.upload_selector_edit, 1)
        hs = QLabel(f"❓ {HELP_SELECTOR}  |  {HELP_FIND_SELECTOR}")
        hs.setStyleSheet("color:#666")
        row_sel.addWidget(hs)
        basic.addRow("上传选择器：", row_sel)

        layout.addLayout(basic)
        layout.addWidget(QLabel("备注："))
        layout.addWidget(self.notes_edit)

        # 步骤列表
        layout.addWidget(QLabel("发布流程步骤（按顺序执行）："))
        steps_h = QHBoxLayout()
        left = QVBoxLayout()
        self.step_list = QListWidget()
        left.addWidget(self.step_list, 1)

        ops = QHBoxLayout()
        self.btn_add_step = QPushButton("新增步骤")
        self.btn_add_step.clicked.connect(self.on_add_step)
        self.btn_up_step = QPushButton("上移")
        self.btn_up_step.clicked.connect(self.on_up_step)
        self.btn_down_step = QPushButton("下移")
        self.btn_down_step.clicked.connect(self.on_down_step)
        self.btn_del_step = QPushButton("删除步骤")
        self.btn_del_step.clicked.connect(self.on_del_step)
        for b in (self.btn_add_step, self.btn_up_step, self.btn_down_step, self.btn_del_step):
            ops.addWidget(b)
        left.addLayout(ops)

        steps_h.addLayout(left, 2)

        # 步骤详情编辑
        right = QVBoxLayout()
        self.step_name = QComboBox()
        self.step_name.setEditable(True)
        self.step_name.addItems(DEFAULT_STEPS)

        self.action_type = QComboBox()
        for k, label in ACTION_LIST:
            self.action_type.addItem(label, k)

        self.selector_value = QLineEdit()
        self.fill_from = QComboBox()
        self.fill_from.addItems(FILL_FROM_LIST)

        self.template_path = QLineEdit()
        self.template_path.setReadOnly(True)
        self.btn_pick_tpl = QPushButton("选择模板图片")
        self.btn_pick_tpl.clicked.connect(self.on_pick_template)

        frm = QFormLayout()
        frm.addRow("步骤名称：", self.step_name)
        frm.addRow("动作类型：", self.action_type)
        frm.addRow("选择器 (XPath/CSS)：", self.selector_value)
        frm.addRow("输入来源：", self.fill_from)
        frm.addRow("模板文件：", self.template_path)
        frmNote = QLabel("说明：选择“视觉模板”类动作时需要模板图片；选择“DOM选择器”类动作时填写选择器，模板可留空。")
        frmNote.setStyleSheet("color:#666")
        right.addLayout(frm)
        right.addWidget(frmNote)
        steps_h.addLayout(right, 3)

        layout.addLayout(steps_h)

        # 保存/取消
        btn_line = QHBoxLayout()
        self.btn_save = QPushButton("保存平台配置")
        self.btn_save.clicked.connect(self.on_save)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_line.addStretch()
        btn_line.addWidget(self.btn_save)
        btn_line.addWidget(self.btn_cancel)
        layout.addLayout(btn_line)

        # 事件
        self.step_list.currentItemChanged.connect(self.on_step_selected)
        self.step_name.currentTextChanged.connect(self.on_step_fields_changed)
        self.action_type.currentIndexChanged.connect(self.on_step_fields_changed)
        self.selector_value.textChanged.connect(self.on_step_fields_changed)
        self.fill_from.currentIndexChanged.connect(self.on_step_fields_changed)

        self.setLayout(layout)
        self._steps = []  # 内存中的步骤列表

    def _load_initial(self, cfg: dict):
        self.login_url_edit.setText(cfg.get("login_url",""))
        self.editor_url_edit.setText(cfg.get("editor_url",""))
        self.upload_selector_edit.setText(cfg.get("upload_selector",""))
        self.notes_edit.setPlainText(cfg.get("notes",""))
        self._steps = cfg.get("steps", [])
        self._refresh_step_list()

    # ---------- 步骤操作 ----------
    def _refresh_step_list(self):
        self.step_list.clear()
        for s in self._steps:
            item = QListWidgetItem(f"{s.get('step_name','未命名')}  |  {s.get('action','')}")
            item.setData(Qt.UserRole, s)
            self.step_list.addItem(item)
        if self.step_list.count() > 0:
            self.step_list.setCurrentRow(0)
        else:
            self._clear_step_editor()

    def _clear_step_editor(self):
        self.step_name.setCurrentIndex(0)
        self.action_type.setCurrentIndex(0)
        self.selector_value.clear()
        self.fill_from.setCurrentIndex(0)
        self.template_path.clear()

    def on_add_step(self):
        s = {
            "step_name": self.step_name.currentText() or "新步骤",
            "action": self.action_type.currentData(),
            "selector": self.selector_value.text().strip(),
            "fill_from": self.fill_from.currentText(),
            "template_path": self.template_path.text().strip()
        }
        self._steps.append(s)
        self._refresh_step_list()
        self.step_list.setCurrentRow(self.step_list.count()-1)

    def on_up_step(self):
        row = self.step_list.currentRow()
        if row <= 0: return
        self._steps[row-1], self._steps[row] = self._steps[row], self._steps[row-1]
        self._refresh_step_list()
        self.step_list.setCurrentRow(row-1)

    def on_down_step(self):
        row = self.step_list.currentRow()
        if row < 0 or row >= len(self._steps)-1: return
        self._steps[row+1], self._steps[row] = self._steps[row], self._steps[row+1]
        self._refresh_step_list()
        self.step_list.setCurrentRow(row+1)

    def on_del_step(self):
        row = self.step_list.currentRow()
        if row < 0: return
        self._steps.pop(row)
        self._refresh_step_list()

    def on_step_selected(self, cur, prev):
        if not cur:
            self._clear_step_editor(); return
        s = cur.data(Qt.UserRole) or {}
        # load fields
        # step_name 用 setEditText 以兼容自定义文本
        self.step_name.setEditText(s.get("step_name",""))
        # action
        action = s.get("action","click_template")
        idx = max(0, [a[0] for a in ACTION_LIST].index(action) if action in [a[0] for a in ACTION_LIST] else 0)
        self.action_type.setCurrentIndex(idx)
        self.selector_value.setText(s.get("selector",""))
        ff = s.get("fill_from","")
        if ff in FILL_FROM_LIST:
            self.fill_from.setCurrentIndex(FILL_FROM_LIST.index(ff))
        else:
            self.fill_from.setCurrentIndex(0)
        self.template_path.setText(s.get("template_path",""))

    def on_step_fields_changed(self, *args):
        row = self.step_list.currentRow()
        if row < 0 or row >= len(self._steps): return
        s = self._steps[row]
        s["step_name"] = self.step_name.currentText()
        s["action"] = self.action_type.currentData()
        s["selector"] = self.selector_value.text().strip()
        s["fill_from"] = self.fill_from.currentText()
        s["template_path"] = self.template_path.text().strip()
        # 更新可视名称
        self.step_list.item(row).setText(f"{s.get('step_name','未命名')}  |  {s.get('action','')}")

    def on_pick_template(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先填写平台名称")
            return
        fn, _ = QFileDialog.getOpenFileName(self, "选择模板图片", "", "Images (*.png *.jpg *.bmp)")
        if not fn:
            return
        try:
            saved = add_template_file(name, fn)
            self.template_path.setText(saved)
            self.on_step_fields_changed()
            QMessageBox.information(self, "已保存", f"模板已保存：\n{saved}")
        except Exception as e:
            QMessageBox.warning(self, "失败", str(e))

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
            "notes": self.notes_edit.toPlainText().strip(),
            "steps": self._steps
        }
        add_or_update_platform(name, cfg)
        QMessageBox.information(self, "成功", f"平台 [{name}] 配置已保存")
        self.accept()
