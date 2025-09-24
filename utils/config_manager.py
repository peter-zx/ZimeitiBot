# -*- coding: utf-8 -*-
"""
utils/config_manager.py
平台配置持久化 & 模板存储（按步骤绑定）
"""
import json
from pathlib import Path
import shutil

ROOT = Path.cwd()
CONFIG_DIR = ROOT / "config"
PLATFORMS_FILE = CONFIG_DIR / "platforms.json"
TEMPLATES_DIR = CONFIG_DIR / "templates"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_STEPS = [
    "打开发布入口", "选择上传图文", "点击上传", "填写标题", "填写正文", "发布"
]

def load_platforms() -> dict:
    if not PLATFORMS_FILE.exists():
        return {}
    try:
        return json.loads(PLATFORMS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_platforms(data: dict):
    PLATFORMS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_or_update_platform(name: str, cfg: dict):
    data = load_platforms()
    data[name] = cfg
    save_platforms(data)

def delete_platform(name: str):
    data = load_platforms()
    if name in data:
        data.pop(name)
        save_platforms(data)
    p = TEMPLATES_DIR / name
    if p.exists() and p.is_dir():
        try:
            shutil.rmtree(p)
        except Exception:
            pass

def ensure_platform_dir(name: str) -> Path:
    d = TEMPLATES_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d

def add_template_file(platform_name: str, src_path: str) -> str:
    """复制模板文件到平台目录，返回保存路径"""
    ensure_platform_dir(platform_name)
    src = Path(src_path)
    if not src.exists():
        raise FileNotFoundError(src_path)
    dst = (TEMPLATES_DIR / platform_name / src.name)
    # 不覆盖：重名则追加编号
    i = 1
    while dst.exists():
        dst = TEMPLATES_DIR / platform_name / f"{src.stem}_{i}{src.suffix}"
        i += 1
    shutil.copy(src, dst)
    return str(dst)

def list_step_templates(platform_name: str, cfg: dict) -> list:
    """读取 steps 中每个步骤的模板路径（有些步骤可能用 selector，没有模板）"""
    steps = cfg.get("steps", [])
    out = []
    for s in steps:
        if "template_path" in s and s["template_path"]:
            out.append(s["template_path"])
    return out
