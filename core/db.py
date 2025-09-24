import os, sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / 'data' / 'app.db'
SCHEMA_PATH = Path(__file__).resolve().parent / 'schema.sql'


class DB:
def __init__(self, db_path=DB_PATH):
self.db_path = Path(db_path)
self.db_path.parent.mkdir(parents=True, exist_ok=True)
self._init()


def _init(self):
with sqlite3.connect(self.db_path) as conn:
conn.execute('PRAGMA foreign_keys=ON;')
schema = SCHEMA_PATH.read_text(encoding='utf-8')
conn.executescript(schema)


def connect(self):
conn = sqlite3.connect(self.db_path)
conn.row_factory = sqlite3.Row
return conn


# ===== Users =====
def get_user(self, username):
with self.connect() as c:
cur = c.execute('SELECT * FROM users WHERE username=?', (username,))
return cur.fetchone()


def create_user(self, username, password):
with self.connect() as c:
c.execute('INSERT INTO users(username,password) VALUES(?,?)', (username, password))
c.commit()


# ===== Tasks =====
def list_tasks(self):
with self.connect() as c:
cur = c.execute('SELECT * FROM tasks ORDER BY id DESC')
return [dict(r) for r in cur.fetchall()]


def get_task(self, task_id:int):
with self.connect() as c:
cur = c.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
r = cur.fetchone()
return dict(r) if r else None


def add_task(self, platform, title, content, media_paths, schedule_at=None):
with self.connect() as c:
cur = c.execute(
'INSERT INTO tasks(platform,title,content,media_paths,schedule_at) VALUES(?,?,?,?,?)',
(platform, title, content, media_paths, schedule_at))
c.commit()
return cur.lastrowid


def update_task(self, task_id, **fields):
if not fields:
return
cols = ','.join(f"{k}=?" for k in fields.keys())
params = list(fields.values()) + [task_id]
with self.connect() as c:
c.execute(f'UPDATE tasks SET {cols} WHERE id=?', params)
c.commit()


def delete_task(self, task_id):
with self.connect() as c:
c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
c.commit()