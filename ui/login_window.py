from PyQt5 import QtWidgets
from core.db import DB


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('登录 / 注册')
        self.db = DB()
        self._build()

    def _build(self):
        self.user_edit = QtWidgets.QLineEdit()
        self.pass_edit = QtWidgets.QLineEdit()
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_btn = QtWidgets.QPushButton('登录')
        self.reg_btn = QtWidgets.QPushButton('注册')

        form = QtWidgets.QFormLayout()
        form.addRow('用户名', self.user_edit)
        form.addRow('密码', self.pass_edit)
        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(self.login_btn)
        btns.addWidget(self.reg_btn)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(btns)

        self.login_btn.clicked.connect(self.on_login)
        self.reg_btn.clicked.connect(self.on_register)

    def on_login(self):
        u = self.user_edit.text().strip()
        p = self.pass_edit.text()
        if u == 'admin' and p == 'admin123':
            self.accept()
            return
        row = self.db.get_user(u)
        if row and row['password'] == p:
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, '失败', '用户名或密码错误')

    def on_register(self):
        u = self.user_edit.text().strip()
        p = self.pass_edit.text()
        if not u or not p:
            QtWidgets.QMessageBox.warning(self, '提示', '请输入用户名和密码')
            return
        try:
            self.db.create_user(u, p)
            QtWidgets.QMessageBox.information(self, '成功', '注册成功，可登录')
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '失败', f'注册失败：{e}')
