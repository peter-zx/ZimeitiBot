import sys
from PyQt5.QtWidgets import QApplication
from ui.login_ui import LoginWindow
from ui.main_ui import MainWindow

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()

    # 这里暂时直接打开主界面，后续可以加登录验证
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
