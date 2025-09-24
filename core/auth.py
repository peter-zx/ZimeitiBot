# -*- coding: utf-8 -*-
# core/auth.py
import sqlite3
import os
import hashlib, binascii
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"

def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def _hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        import os as _os
        salt = _os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def _verify_password(stored: str, password: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return binascii.hexlify(dk).decode() == hash_hex
    except Exception:
        return False

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    if not username or not password:
        return False, "用户名和密码不能为空"
    conn = _get_conn()
    cur = conn.cursor()
    try:
        # 检查是否存在
        cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
        if cur.fetchone():
            return False, "用户名已存在"
        pw = _hash_password(password)
        cur.execute("INSERT INTO users(username,email,password_hash) VALUES(?,?,?)",
                    (username, email, pw))
        conn.commit()
        return True, "注册成功"
    except sqlite3.Error as e:
        return False, f"数据库错误: {e}"
    finally:
        conn.close()

def verify_user(username: str, password: str) -> tuple[bool, str]:
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return False, "用户不存在"
        ok = _verify_password(row["password_hash"], password)
        if ok:
            return True, "验证通过"
        return False, "密码错误"
    except sqlite3.Error as e:
        return False, f"数据库错误: {e}"
    finally:
        conn.close()

def ensure_default_admin():
    """首次启动创建默认管理员：admin/admin123（若不存在）"""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username='admin'")
    if not cur.fetchone():
        pw = _hash_password("admin123")
        cur.execute("INSERT INTO users(username,email,password_hash,role) VALUES(?,?,?,?)",
                    ("admin", "admin@example.com", pw, "admin"))
        conn.commit()
    conn.close()
