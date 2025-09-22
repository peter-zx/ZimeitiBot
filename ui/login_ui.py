<<<<<<< HEAD
# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from ui.main_ui import MainWindow

# 测试管理员账号
USERS = {"admin": "admin123"}
=======
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
>>>>>>> ce80e5302e41d8bd1ff7348442b2c7bac06778b6

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD
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
=======
        self.setWindowTitle("自媒体助手 - 登录")
        self.resize(300, 200)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("账号:"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("密码:"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.login_btn = QPushButton("登录/扫码登录")
        layout.addWidget(self.login_btn)

        self.setLayout(layout)
>>>>>>> ce80e5302e41d8bd1ff7348442b2c7bac06778b6
