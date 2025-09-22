# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from ui.login_ui import LoginWindow

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("注册 - 自媒体助手")
        self.setGeometry(300, 150, 400, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("用户名:")
        self.username = QLineEdit()
        self.label2 = QLabel("邮箱:")
        self.email = QLineEdit()
        self.label3 = QLabel("密码:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.label4 = QLabel("确认密码:")
        self.password2 = QLineEdit()
        self.password2.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.register)

        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.label2)
        layout.addWidget(self.email)
        layout.addWidget(self.label3)
        layout.addWidget(self.password)
        layout.addWidget(self.label4)
        layout.addWidget(self.password2)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def register(self):
        u = self.username.text()
        p1 = self.password.text()
        p2 = self.password2.text()
        if p1 != p2:
            QMessageBox.warning(self, "错误", "两次密码不一致")
            return
        # 简单演示，实际应保存到数据库
        QMessageBox.information(self, "成功", f"账号 {u} 注册成功，请登录")
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
