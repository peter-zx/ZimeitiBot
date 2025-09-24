# main_app.py
import sys
from PyQt5 import QtWidgets
from ui.login_window import LoginWindow
from ui.main_ui import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)

    login = LoginWindow()
    if login.exec_() != QtWidgets.QDialog.Accepted:
        sys.exit(0)

    w = MainWindow()
    w.resize(1100, 720)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
