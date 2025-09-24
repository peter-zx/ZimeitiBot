from PyQt5 import QtWidgets
from datetime import datetime


class TaskDialog(QtWidgets.QDialog):
def __init__(self, parent=None, init_data=None):
super().__init__(parent)
self.setWindowTitle('新建/编辑任务')
self._build(init_data or {})


def _build(self, init):
self.platform = QtWidgets.QComboBox(); self.platform.addItems(['xiaohongshu'])
self.title = QtWidgets.QLineEdit()
self.content = QtWidgets.QPlainTextEdit()
self.media = QtWidgets.QLineEdit()
self.schedule = QtWidgets.QDateTimeEdit(); self.schedule.setCalendarPopup(True)
self.schedule.setDateTime(datetime.now())
self.schedule.setSpecialValueText('立即')


if init:
self.platform.setCurrentText(init.get('platform','xiaohongshu'))
self.title.setText(init.get('title',''))
self.content.setPlainText(init.get('content',''))
self.media.setText(init.get('media_paths',''))


form = QtWidgets.QFormLayout()
form.addRow('平台', self.platform)
form.addRow('标题', self.title)
form.addRow('正文', self.content)
form.addRow('媒体路径(;分隔)', self.media)
form.addRow('计划时间(可空)', self.schedule)


ok = QtWidgets.QPushButton('确定'); cancel = QtWidgets.QPushButton('取消')
ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
btns = QtWidgets.QHBoxLayout(); btns.addStretch(1); btns.addWidget(ok); btns.addWidget(cancel)


v = QtWidgets.QVBoxLayout(self)
v.addLayout(form); v.addLayout(btns)


def value(self):
dt = self.schedule.dateTime().toString('yyyy-MM-dd HH:mm:ss')
return {
'platform': self.platform.currentText(),
'title': self.title.text(),
'content': self.content.toPlainText(),
'media_paths': self.media.text(),
'schedule_at': dt if self.schedule.dateTime() else None,
}