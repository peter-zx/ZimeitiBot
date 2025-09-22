from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自媒体助手 - 主界面")
        self.resize(400, 300)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("选择平台:"))
        self.platform_label = QLabel("小红书")
        layout.addWidget(self.platform_label)

        layout.addWidget(QLabel("模板截图配置:"))
        self.publish_btn = QPushButton("发布按钮模板")
        self.upload_btn = QPushButton("上传图文按钮模板")
        self.submit_btn = QPushButton("发布按钮模板")
        layout.addWidget(self.publish_btn)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.submit_btn)

        layout.addWidget(QLabel("任务计划:"))
        self.task_btn = QPushButton("加载任务 Excel")
        self.run_btn = QPushButton("开始上传")
        layout.addWidget(self.task_btn)
        layout.addWidget(self.run_btn)

        self.setLayout(layout)
