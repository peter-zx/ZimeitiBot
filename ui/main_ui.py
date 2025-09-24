from PyQt5 import QtWidgets, QtCore
from core.db import DB
from core.executor import Runner
from ui.task_dialog import TaskDialog
from pathlib import Path


class MainWindow(QtWidgets.QMainWindow):
def __init__(self):
super().__init__()
self.setWindowTitle('自媒体自动化助手 - MVP')
self.db = DB()
self._build()
self._load_tasks()


def _build(self):
# 任务表
self.table = QtWidgets.QTableWidget(0, 6)
self.table.setHorizontalHeaderLabels(['ID','平台','标题','状态','计划时间','操作'])
self.table.horizontalHeader().setStretchLastSection(True)


# 按钮
self.btn_add = QtWidgets.QPushButton('新建任务')
self.btn_refresh = QtWidgets.QPushButton('刷新')
self.btn_run = QtWidgets.QPushButton('运行选中任务')


top = QtWidgets.QHBoxLayout(); top.addWidget(self.btn_add); top.addWidget(self.btn_refresh); top.addWidget(self.btn_run); top.addStretch(1)


# 日志区
self.log = QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True)


central = QtWidgets.QWidget(); v = QtWidgets.QVBoxLayout(central)
v.addLayout(top); v.addWidget(self.table); v.addWidget(QtWidgets.QLabel('执行日志')); v.addWidget(self.log)
self.setCentralWidget(central)


# 连接
self.btn_add.clicked.connect(self.on_add)
self.btn_refresh.clicked.connect(self._load_tasks)
self.btn_run.clicked.connect(self.on_run)


def _load_tasks(self):
tasks = self.db.list_tasks()
self.table.setRowCount(0)
for r in tasks:
row = self.table.rowCount(); self.table.insertRow(row)
self.table.setItem(row,0, QtWidgets.QTableWidgetItem(str(r['id'])))
self.table.setItem(row,1, QtWidgets.QTableWidgetItem(r['platform']))
self.table.setItem(row,2, QtWidgets.QTableWidgetItem(r.get('title') or ''))
self.table.setItem(row,3, QtWidgets.QTableWidgetItem(r['status']))
self.table.setItem(row,4, QtWidgets.QTableWidgetItem(r.get('schedule_at') or ''))
btn_del = QtWidgets.QPushButton('删除'); btn_del.clicked.connect(lambda _, tid=r['id']: self.on_delete(tid))
w = QtWidgets.QWidget(); layout = QtWidgets.QHBoxLayout(w); layout.setContentsMargins(0,0,0,0); layout.addWidget(btn_del); layout.addStretch(1)
self.table.setCellWidget(row,5,w)


def on_add(self):
dlg = TaskDialog(self)
if dlg.exec_() == QtWidgets.QDialog.Accepted:
v = dlg.value()
self.db.add_task(v['platform'], v['title'], v['content'], v['media_paths'], v['schedule_at'])
self._load_tasks()


def on_delete(self, task_id):
self.db.delete_task(task_id)
self._load_tasks()


def on_run(self):
self._load_tasks()