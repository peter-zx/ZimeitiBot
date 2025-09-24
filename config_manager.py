# -*- coding: utf-8 -*-
"""
utils/config_manager.py
管理平台配置与模板的持久化：
- config/platforms.json 保存平台配置
- config/templates/<platform>/ 保存模板图片
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
    # 同步删除模板目录
    p = TEMPLATES_DIR / name
    if p.exists() and p.is_dir():
        try:
            shutil.rmtree(p)
        except Exception:
            pass

def list_templates(name: str):
    d = TEMPLATES_DIR / name
    if not d.exists():
        return []
    return [str(p) for p in sorted(d.iterdir()) if p.is_file()]

def add_template(name: str, file_path: str) -> str:
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(file_path)
    dst_dir = TEMPLATES_DIR / name
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    # 如已存在，避免覆盖
    if dst.exists():
        dst = dst_dir / f"{src.stem}_copy{src.suffix}"
    shutil.copy(src, dst)
    return str(dst)
