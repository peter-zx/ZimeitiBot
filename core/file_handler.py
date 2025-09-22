# -*- coding: utf-8 -*-
import openpyxl
import os

class FileHandler:
    def __init__(self, excel_file):
        self.excel_file = excel_file

    def get_tasks(self):
        wb = openpyxl.load_workbook(self.excel_file)
        sheet = wb.active
        tasks = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            img_path, title, content, pub_time = row
            tasks.append({
                "image": os.path.join("tasks", img_path),
                "title": title,
                "content": content,
                "time": pub_time
            })
        return tasks
