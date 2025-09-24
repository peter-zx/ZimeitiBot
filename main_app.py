# -*- coding: utf-8 -*-
"""
main_app.py - 项目入口
启动自媒体助手，显示登录窗口
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
