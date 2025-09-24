PRAGMA journal_mode=WAL;


CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS tasks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
platform TEXT NOT NULL, -- 平台 key（如 xiaohongshu）
title TEXT,
content TEXT,
media_paths TEXT, -- 用 ; 分隔的本地文件绝对路径
schedule_at TEXT, -- 计划发布时间，ISO 字符串，可空（立即执行）
status TEXT DEFAULT 'pending', -- pending|running|done|failed
created_at TEXT DEFAULT (datetime('now')),
updated_at TEXT DEFAULT (datetime('now'))
);


CREATE TRIGGER IF NOT EXISTS trg_tasks_updated_at
AFTER UPDATE ON tasks
FOR EACH ROW BEGIN
UPDATE tasks SET updated_at = datetime('now') WHERE id = old.id;
END;