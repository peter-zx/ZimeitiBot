# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication
from ui.startup_ui import StartupWindow

def main():
    app = QApplication(sys.argv)
    window = StartupWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
