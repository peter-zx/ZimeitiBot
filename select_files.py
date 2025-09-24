import sys, os, zipfile
from pathlib import Path
from PyQt5 import QtWidgets, QtCore

class FileSelector(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("项目文件选择器")
        self.resize(700, 550)

        layout = QtWidgets.QVBoxLayout(self)

        # 路径输入
        path_layout = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit(str(Path.cwd()))
        self.browse_btn = QtWidgets.QPushButton("浏览")
        path_layout.addWidget(QtWidgets.QLabel("根目录:"))
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)

        # 树形控件
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["文件/目录", "路径"])
        self.tree.setColumnWidth(0, 300)
        layout.addWidget(self.tree)

        # 按钮
        btn_layout = QtWidgets.QHBoxLayout()
        self.export_btn = QtWidgets.QPushButton("导出选中文件为zip")
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_btn)
        layout.addLayout(btn_layout)

        # 信号
        self.browse_btn.clicked.connect(self.choose_folder)
        self.export_btn.clicked.connect(self.export_zip)

        # 初始化
        self.load_tree(Path(self.path_edit.text()))

    def load_tree(self, root: Path):
        self.tree.clear()
        def add_items(parent, path):
            for child in sorted(path.iterdir()):
                item = QtWidgets.QTreeWidgetItem(parent, [child.name, str(child)])
                item.setCheckState(0, QtCore.Qt.Unchecked)
                if child.is_dir():
                    add_items(item, child)
        add_items(self.tree.invisibleRootItem(), root)

    def choose_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "选择根目录", self.path_edit.text())
        if folder:
            self.path_edit.setText(folder)
            self.load_tree(Path(folder))

    def collect_checked(self):
        files = []
        def walk(item):
            for i in range(item.childCount()):
                child = item.child(i)
                if child.checkState(0) == QtCore.Qt.Checked:
                    p = Path(child.text(1))
                    if p.is_file():
                        files.append(p)
                walk(child)
        walk(self.tree.invisibleRootItem())
        return files

    def export_zip(self):
        files = self.collect_checked()
        if not files:
            QtWidgets.QMessageBox.warning(self, "提示", "没有选中文件")
            return
        zip_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存为", "selected_files.zip", "Zip文件 (*.zip)")
        if not zip_path:
            return
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in files:
                arcname = Path(f).relative_to(Path(self.path_edit.text()))
                zf.write(f, arcname)
        QtWidgets.QMessageBox.information(self, "完成", f"已导出 {len(files)} 个文件到 {zip_path}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = FileSelector()
    w.show()
    sys.exit(app.exec_())
