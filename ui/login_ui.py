from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
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
