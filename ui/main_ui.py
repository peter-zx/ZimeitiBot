# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"自媒体助手 - 欢迎 {self.username}")
        self.setGeometry(100, 50, 1000, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # 左侧配置区
        config_layout = QVBoxLayout()
        config_layout.addWidget(QLabel("平台配置区域"))
        self.platform_list = QListWidget()
        self.platform_list.addItem("小红书")
        config_layout.addWidget(self.platform_list)
        self.configure_btn = QPushButton("配置平台按钮 / URL")
        config_layout.addWidget(self.configure_btn)

        # 中间任务区
        task_layout = QVBoxLayout()
        task_layout.addWidget(QLabel("任务区域"))
        self.task_list = QListWidget()
        task_layout.addWidget(self.task_list)
        self.new_task_btn = QPushButton("新建任务")
        task_layout.addWidget(self.new_task_btn)

        # 右侧执行区
        execute_layout = QVBoxLayout()
        execute_layout.addWidget(QLabel("执行区域"))
        self.run_btn = QPushButton("开始执行任务")
        execute_layout.addWidget(self.run_btn)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        execute_layout.addWidget(self.log_view)

        main_layout.addLayout(config_layout, 2)
        main_layout.addLayout(task_layout, 3)
        main_layout.addLayout(execute_layout, 2)

        self.setLayout(main_layout)
