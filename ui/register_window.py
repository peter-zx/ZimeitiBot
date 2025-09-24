# -*- coding: utf-8 -*-
# ui/register_window.py
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from core.auth import register_user

class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("注册 - 自媒体助手")
        self.resize(420, 360)
        self._build()

    def _build(self):
        self.label_user = QLabel("用户名：")
        self.input_user = QLineEdit()
        self.label_mail = QLabel("邮箱（可选）：")
        self.input_mail = QLineEdit()
        self.label_p1 = QLabel("密码：")
        self.input_p1 = QLineEdit(); self.input_p1.setEchoMode(QLineEdit.Password)
        self.label_p2 = QLabel("确认密码：")
        self.input_p2 = QLineEdit(); self.input_p2.setEchoMode(QLineEdit.Password)

        self.btn_ok = QPushButton("注册")
        layout = QVBoxLayout()
        for w in (self.label_user, self.input_user, self.label_mail, self.input_mail,
                  self.label_p1, self.input_p1, self.label_p2, self.input_p2, self.btn_ok):
            layout.addWidget(w)
        self.setLayout(layout)

        self.btn_ok.clicked.connect(self.on_register)

    def on_register(self):
        u = self.input_user.text().strip()
        m = self.input_mail.text().strip()
        p1 = self.input_p1.text()
        p2 = self.input_p2.text()
        if not u or not p1:
            QMessageBox.warning(self, "错误", "用户名/密码不能为空")
            return
        if p1 != p2:
            QMessageBox.warning(self, "错误", "两次密码不一致")
            return
        ok, msg = register_user(u, m, p1)
        if ok:
            QMessageBox.information(self, "成功", "注册成功，请返回登录")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", msg)
