import streamlit as st
import os, zipfile
from pathlib import Path

def zip_files(files, base_dir, out_path):
    with zipfile.ZipFile(out_path, "w") as zf:
        for f in files:
            arcname = Path(f).relative_to(base_dir)
            zf.write(f, arcname)

st.title("在线文件选择器")

folder = st.text_input("输入目录路径", str(Path.cwd()))
if Path(folder).exists():
    all_files = [str(p) for p in Path(folder).rglob("*.py")]  # 默认列出 .py 文件
    selected = st.multiselect("选择要打包的文件", all_files)
    if st.button("导出zip"):
        out = Path("selected_files.zip")
        zip_files(selected, Path(folder), out)
        with open(out, "rb") as f:
            st.download_button("下载zip", f, file_name="selected_files.zip")
