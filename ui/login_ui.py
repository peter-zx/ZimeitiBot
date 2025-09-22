# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from ui.main_ui import MainWindow

# 测试管理员账号
USERS = {"admin": "admin123"}

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录 - 自媒体助手")
        self.setGeometry(300, 150, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("用户名:")
        self.username = QLineEdit()
        self.label2 = QLabel("密码:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login)

        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.label2)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def login(self):
        user = self.username.text()
        pwd = self.password.text()
        if user in USERS and USERS[user] == pwd:
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "错误", "账号或密码错误")
