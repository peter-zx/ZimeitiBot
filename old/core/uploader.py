# core/uploader.py
import os
import sqlite3
import datetime
from typing import List, Tuple
from utils.logger import get_logger
from utils.helpers import human_sleep

logger = get_logger("core.uploader")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "upload_history.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            platform TEXT,
            status TEXT,
            message TEXT,
            ts TEXT
        )
        """)
        conn.commit()
    except Exception as e:
        logger.exception("init_db failed: %s", e)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass

def record_upload(file_path: str, platform: str, status: str, message: str = ""):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO uploads (file_path, platform, status, message, ts) VALUES (?, ?, ?, ?, ?)",
            (file_path, platform, status, message, datetime.datetime.now().isoformat())
        )
        conn.commit()
    except Exception as e:
        logger.exception("record_upload failed: %s", e)
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass

# 平台驱动延后导入（避免循环依赖问题）
try:
    from platforms.xiaohongshu import XiaoHongShu
except Exception:
    XiaoHongShu = None

class Uploader:
    def __init__(self, driver):
        self.driver = driver
        self.platform = XiaoHongShu(driver) if XiaoHongShu else None
        init_db()

    def batch_upload_folder(self, folder: str, limit: int = None) -> List[Tuple[str, bool]]:
        if not os.path.isdir(folder):
            raise ValueError(f"folder not found: {folder}")
        files = [os.path.join(folder, f) for f in sorted(os.listdir(folder))
                 if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(('.mp4','.mov','.jpg','.jpeg','.png'))]
        if limit:
            files = files[:limit]
        results = []
        for fp in files:
            try:
                if not self.platform:
                    logger.error("platform driver not available")
                    record_upload(fp, "unknown", "error", "platform unavailable")
                    results.append((fp, False))
                    continue
                ok = self.platform.upload_one_file(fp, caption="", title=os.path.basename(fp))
                if ok:
                    record_upload(fp, "xiaohongshu", "success", "uploaded")
                    logger.info("uploaded: %s", fp)
                    results.append((fp, True))
                else:
                    record_upload(fp, "xiaohongshu", "failed", "upload returned False")
                    logger.warning("upload returned False: %s", fp)
                    results.append((fp, False))
            except Exception as e:
                record_upload(fp, "xiaohongshu", "error", str(e))
                logger.exception("upload exception: %s -> %s", fp, e)
                results.append((fp, False))
            human_sleep(2.0, 4.0)
        return results
