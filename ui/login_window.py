# -*- coding: utf-8 -*-
# ui/login_window.py
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from core.auth import verify_user, init_auth_db, ensure_default_admin
from ui.main_ui import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自媒体助手 - 登录")
        self.resize(420, 320)
        init_auth_db()
        ensure_default_admin()
        self._build()

    def _build(self):
        self.label_user = QLabel("账号：")
        self.input_user = QLineEdit()
        self.label_pass = QLabel("密码：")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("登录")
        self.btn_register = QPushButton("注册")

        layout = QVBoxLayout()
        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

        self.btn_login.clicked.connect(self.do_login)
        self.btn_register.clicked.connect(self.open_register)

    def do_login(self):
        user = self.input_user.text().strip()
        pwd = self.input_pass.text().strip()
        ok, msg = verify_user(user, pwd)
        if ok:
            self._into_main(user)
        else:
            QMessageBox.warning(self, "登录失败", msg)

    def open_register(self):
        from ui.register_window import RegisterWindow
        dlg = RegisterWindow(self)
        dlg.exec_()

    def _into_main(self, username: str):
        self.main_win = MainWindow(username=username)
        self.main_win.show()
        self.close()
