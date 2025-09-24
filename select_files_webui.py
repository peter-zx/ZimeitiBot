import gradio as gr
import zipfile
from pathlib import Path

# ===== 配置 =====
QR_PATH = r"qrcode.jpg"
DEFAULT_ROOT = str(Path.cwd())
DEFAULT_EXTS = [".py"]
ALL_EXT_CHOICES = [
    ".py", ".txt", ".md", ".json", ".yaml", ".yml",
    ".csv", ".xls", ".xlsx",
    ".html", ".css", ".js", ".ts",
    ".sql", ".xml", ".log",
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    "*（全部）"
]
# ================

def _make_glob(exts: list[str]) -> str:
    if (not exts) or ("*（全部）" in exts):
        return "**/*"
    if len(exts) == 1:
        return f"**/*{exts[0]}"
    return "{" + ",".join(f"**/*{e}" for e in exts) + "}"

def update_explorer(root_dir: str, exts: list[str]):
    root = Path(root_dir.strip()) if root_dir else Path(DEFAULT_ROOT)
    if not root.exists() or not root.is_dir():
        return gr.update(label=f"⚠️ 无效路径：{root}", value=None, root_dir=str(Path.cwd()), glob="**/*")
    return gr.update(root_dir=str(root), glob=_make_glob(exts), label=f"文件浏览器（目录：{root}）")

def zip_selected(root_dir: str, _exts: list[str], files: list[str] | None):
    if not files:
        return None, "⚠️ 还没有选择任何文件。"
    root = Path(root_dir.strip()) if root_dir else Path(DEFAULT_ROOT)
    out = Path.cwd() / "selected_files.zip"
    if out.exists():
        try:
            out.unlink()
        except Exception:
            out = Path.cwd() / "selected_files_2.zip"
    count = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            p = Path(f)
            if not p.exists() or not p.is_file():
                continue
            try:
                arcname = p.relative_to(root)
            except Exception:
                arcname = p.name
            zf.write(p, arcname)
            count += 1
    if count == 0:
        return None, "⚠️ 选中的条目里没有有效文件。"
    return str(out.resolve()), f"✅ 已打包 {count} 个文件 → {out.name}"

with gr.Blocks(
    title="项目文件选择器 - WebUI 版",
    css="""
/* 顶部标题 */
#hero-title { text-align:center; font-size: 40px; font-weight: 800; margin: 10px 0 4px; }
#hero-sub   { text-align:center; font-size: 16px; color:#666; margin-bottom: 24px; }

/* 信息卡片：左文案右二维码 */
#card { 
  display:flex; gap: 24px; justify-content:space-between; align-items:center;
  border: 1px solid #eaeaea; border-radius: 14px; padding: 18px 22px; background: #fafafa;
  margin: 0 0 22px 0;
}
#card-text { font-size:16px; line-height:1.9; }

/* 区段标题 */
.section-title { font-size: 22px; font-weight: 700; margin: 22px 0 8px; }

/* 操作行按钮 */
#btn-pack { font-weight:700; }

/* 底部大下载按钮 */
#dl-wrap { margin-top: 14px; }
#dl-btn  { font-size: 20px !important; height: 64px !important; width: 100%; }
"""
) as demo:

    # —— 顶部 —— #
    gr.HTML('<div id="hero-title">📂 项目文件选择器 - WebUI 版</div>')
    gr.HTML('<div id="hero-sub">AIGC散修_竹相左边 ｜ 只分享验证可行的前沿技术</div>')

    # —— 信息卡片（无重复） —— #
    with gr.Row():
        with gr.Column(scale=3):
            gr.HTML(
                '<div id="card">'
                '<div id="card-text">'
                '<div><b>开发者：</b> AIGC散修_竹相左边</div>'
                '<div><b>定位：</b> 只分享验证可行的前沿技术</div>'
                '<div><b>交流基地：</b> 公众号 <b>明年还要做设计</b></div>'
                '</div>'
                '</div>'
            )
        with gr.Column(scale=1):
            gr.Image(value=QR_PATH, show_label=False, height=180, type="filepath")

    gr.HTML('<div class="section-title">🛠️ 工具使用</div>')

    # —— 工具区 —— #
    root_dir = gr.Textbox(
        value=DEFAULT_ROOT,
        label="根目录路径",
        placeholder="例如：E:/ai_work/zimeitiboot 或 C:/Users/你的用户名/Documents"
    )
    exts = gr.CheckboxGroup(
        choices=ALL_EXT_CHOICES,
        value=DEFAULT_EXTS,
        label="文件格式筛选（可多选）"
    )
    explorer = gr.FileExplorer(
        root_dir=DEFAULT_ROOT,
        glob=_make_glob(DEFAULT_EXTS),
        label="文件浏览器",
        height=430
    )

    # —— 按钮行：刷新 | 打包 —— #
    with gr.Row():
        btn_refresh = gr.Button("🔄 刷新文件树")
        btn_pack = gr.Button("📦 打包（生成 ZIP）", elem_id="btn-pack", variant="primary")

    # 打包状态提示
    status = gr.Markdown("")

    # —— 底部：仅放一个大下载按钮 —— #
    with gr.Row(elem_id="dl-wrap"):
        dl_btn = gr.DownloadButton("⬇️ 立即下载 ZIP", elem_id="dl-btn")

    # —— 交互绑定 —— #
    root_dir.change(fn=update_explorer, inputs=[root_dir, exts], outputs=explorer)
    exts.change(fn=update_explorer, inputs=[root_dir, exts], outputs=explorer)
    btn_refresh.click(fn=update_explorer, inputs=[root_dir, exts], outputs=explorer)

    # 打包 → 设置下载按钮文件 & 状态文案
    btn_pack.click(
        fn=zip_selected,
        inputs=[root_dir, exts, explorer],
        outputs=[dl_btn, status]
    )

demo.launch(share=False)
