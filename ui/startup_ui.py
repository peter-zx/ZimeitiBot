# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from ui.login_ui import LoginWindow
from ui.register_ui import RegisterWindow

class StartupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自媒体助手")
        self.setGeometry(200, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 背景海报
        self.bg_label = QLabel(self)
        pixmap = QPixmap("ui/assets/startup_bg.png")  # 替换成你自己的海报
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)
        layout.addWidget(self.bg_label)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.clicked.connect(self.open_login)
        layout.addWidget(self.login_btn)

        # 注册按钮
        self.register_btn = QPushButton("注册", self)
        self.register_btn.clicked.connect(self.open_register)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()
