# core/file_handler.py
import os
import tkinter as tk
from tkinter import filedialog
from typing import List

class FileHandler:
    def __init__(self, base_folder: str = None):
        self.base_folder = base_folder
        self.files = []

    def select_folder_dialog(self, initialdir: str = ".") -> str:
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="请选择待上传文件夹", initialdir=initialdir)
        root.destroy()
        if folder:
            self.base_folder = folder
        return self.base_folder

    def load_files_from_folder(self, exts: List[str] = None) -> List[str]:
        if not self.base_folder:
            return []
        exts = exts or [".mp4", ".mov", ".jpg", ".jpeg", ".png"]
        files = []
        for fn in sorted(os.listdir(self.base_folder)):
            p = os.path.join(self.base_folder, fn)
            if os.path.isfile(p) and os.path.splitext(fn)[1].lower() in exts:
                files.append(p)
        self.files = files
        return files

    def get_files(self) -> List[str]:
        return list(self.files)
