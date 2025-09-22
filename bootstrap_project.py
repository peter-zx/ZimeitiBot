# -*- coding: utf-8 -*-
"""
bootstrap_project.py
一键生成项目目录与关键模块文件（storage, plugin, plugin_loader, executor, mock plugin, main_app 等）
用法:
  1. 保存为 bootstrap_project.py 到目标目录 (例如 E:\ai_work\zimeitiboot)
  2. 激活虚拟环境
  3. python bootstrap_project.py
  4. python main_app.py 测试
"""

import os
from pathlib import Path
import json
import textwrap

ROOT = Path.cwd()

STRUCT = {
    "config": {
        "plugins.json": None
    },
    "core": {
        "storage.py": None,
        "plugin.py": None,
        "plugin_loader.py": None,
        "executor.py": None
    },
    "platforms": {
        "mock_plugin.py": None
    },
    "data": {},
    "utils": {},
    "tasks": {},
    "main_app.py": None,
    "requirements.txt": None,
    "README.md": None
}

# file contents
FILES = {}

FILES["config/plugins.json"] = json.dumps({
    "plugins": [
        {
            "name": "mock",
            "module": "platforms.mock_plugin",
            "class": "MockPlugin"
        }
    ]
}, indent=2, ensure_ascii=False)

FILES["core/storage.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    \"\"\"core/storage.py
    简单的 SQLite 存储：tasks, events, summaries 表
    用于持久化任务和事件日志
    \"\"\"
    import sqlite3
    from pathlib import Path

    DB_PATH = Path("data/zimeitiboot.db")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    def get_conn():
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_conn()
        cur = conn.cursor()
        cur.executescript(\"\"\"
        CREATE TABLE IF NOT EXISTS tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          platform TEXT,
          image TEXT,
          title TEXT,
          content TEXT,
          schedule_time TEXT,
          status TEXT,
          retries INTEGER DEFAULT 0,
          created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id INTEGER,
          event_time TEXT,
          event_type TEXT,
          payload TEXT
        );
        CREATE TABLE IF NOT EXISTS summaries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          key TEXT,
          summary TEXT,
          created_at TEXT
        );
        \"\"\")
        conn.commit()
        conn.close()

    def insert_task(task):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(\"
          INSERT INTO tasks(platform,image,title,content,schedule_time,status,retries,created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        \", (task.get('platform'), task.get('image'), task.get('title'),
              task.get('content'), task.get('schedule_time'), task.get('status','pending'), task.get('retries',0)))
        task_id = cur.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def append_event(task_id, event_type, payload):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(\"INSERT INTO events(task_id,event_time,event_type,payload) VALUES (?, datetime('now'), ?, ?)\",
                    (task_id, event_type, payload))
        conn.commit()
        conn.close()

    def fetch_recent_events(task_id, limit=20):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(\"SELECT * FROM events WHERE task_id=? ORDER BY id DESC LIMIT ?\", (task_id, limit))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    """)

FILES["core/plugin.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    from abc import ABC, abstractmethod

    class PlatformPluginBase(ABC):
        name = "base"

        def __init__(self, config: dict = None):
            self.config = config or {}

        @abstractmethod
        def open_login(self) -> bool:
            \"\"\"打开登录（扫码或其他），返回是否已触发登录页\"\"\"
            pass

        @abstractmethod
        def navigate_to_editor(self) -> bool:
            \"\"\"导航到发布编辑器页面（视觉或 DOM）\"\"\"
            pass

        @abstractmethod
        def upload_and_publish(self, task: dict) -> dict:
            \"\"\"执行上传并发布，返回 dict: {success: bool, reason: str} \"\"\"
            pass
    """)

FILES["core/plugin_loader.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    import json, importlib
    from pathlib import Path

    def load_plugins(manifest_path='config/plugins.json'):
        path = Path(manifest_path)
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding='utf-8'))
        plugins = {}
        for it in data.get('plugins', []):
            module_name = it.get('module')
            class_name = it.get('class')
            name = it.get('name')
            try:
                mod = importlib.import_module(module_name)
                cls = getattr(mod, class_name)
                plugins[name] = cls
            except Exception as e:
                print(f\"load_plugins: failed to load {module_name}.{class_name}: {e}\")
        return plugins
    """)

FILES["core/executor.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    from core.storage import insert_task, append_event, fetch_recent_events, init_db, get_conn
    from datetime import datetime
    import time

    class Executor:
        def __init__(self, plugin_registry):
            # plugin_registry: dict name -> PluginClass
            self.plugins = plugin_registry

        def submit_task(self, task: dict):
            # persist task and return id
            task_id = insert_task(task)
            append_event(task_id, 'task.created', str(task))
            return task_id

        def execute_task_by_id(self, task_id: int):
            # load task from db
            conn = get_conn()
            cur = conn.cursor()
            cur.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
            row = cur.fetchone()
            if not row:
                return {'success': False, 'reason': 'task_not_found'}
            task = dict(row)
            append_event(task_id, 'executor.start', 'start executing')
            # pick plugin by task.platform
            plugin_name = task.get('platform')
            plugin_cls = self.plugins.get(plugin_name)
            if not plugin_cls:
                append_event(task_id, 'executor.error', f'no plugin for {plugin_name}')
                return {'success': False, 'reason': f'no plugin {plugin_name}'}
            plugin = plugin_cls(config={})
            try:
                # plugin should implement upload_and_publish and return dict
                res = plugin.upload_and_publish(task)
                append_event(task_id, 'executor.finish', str(res))
                # update task status
                cur.execute('UPDATE tasks SET status=? WHERE id=?', ('done' if res.get('success') else 'error', task_id))
                conn.commit()
                return res
            except Exception as e:
                append_event(task_id, 'executor.exception', str(e))
                cur.execute('UPDATE tasks SET status=? WHERE id=?', ('error', task_id))
                conn.commit()
                return {'success': False, 'reason': str(e)}
            finally:
                conn.close()
    """)

FILES["platforms/mock_plugin.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    \"\"\"platforms/mock_plugin.py
    一个不会打开浏览器的 Mock 插件，用于测试 executor 的工作流。
    它会：记录开始/结束并模拟成功。
    \"\"\"
    import time
    from core.plugin import PlatformPluginBase
    from core.storage import append_event

    class MockPlugin(PlatformPluginBase):
        name = 'mock'

        def __init__(self, config=None):
            super().__init__(config or {})

        def open_login(self) -> bool:
            append_event(None, 'mock.open_login', 'noop')
            return True

        def navigate_to_editor(self) -> bool:
            append_event(None, 'mock.navigate_to_editor', 'noop')
            return True

        def upload_and_publish(self, task: dict) -> dict:
            # simulate steps and append events
            tid = task.get('id') or 'unknown'
            append_event(tid, 'mock.start', f\"start mock upload for {task.get('image')}\")
            time.sleep(1)  # simulate work
            append_event(tid, 'mock.upload', f\"uploaded {task.get('image')}\")
            time.sleep(0.5)
            append_event(tid, 'mock.publish', 'published successfully')
            return {'success': True, 'reason': 'mock ok'}
    """)

FILES["main_app.py"] = textwrap.dedent("""\
    # -*- coding: utf-8 -*-
    \"\"\"main_app.py (minimal test runner)
    - 初始化 DB
    - 加载插件 registry
    - 创建 Executor
    - 插入一条示例任务并执行（使用 mock plugin）
    运行: python main_app.py
    \"\"\"
    import time
    from core.storage import init_db, fetch_recent_events
    from core.plugin_loader import load_plugins
    from core.executor import Executor

    def main():
        print('初始化数据库...')
        init_db()
        print('加载插件清单...')
        plugins = load_plugins('config/plugins.json')
        print('插件:', plugins)
        ex = Executor(plugins)
        print('提交示例任务到 executor...')
        task = {
            'platform': 'mock',
            'image': 'tasks/images/example.png',
            'title': '测试标题',
            'content': '这是测试正文',
            'schedule_time': None,
            'status': 'pending',
            'retries': 0
        }
        task_id = ex.submit_task(task)
        print('插入任务 id =', task_id)
        print('执行任务...')
        res = ex.execute_task_by_id(task_id)
        print('执行结果:', res)
        print('最近事件：')
        events = fetch_recent_events(task_id, limit=20)
        for e in events:
            print(e)
        print('done.')

    if __name__ == '__main__':
        main()
    """)

FILES["requirements.txt"] = textwrap.dedent("""\
    PyQt5
    selenium
    webdriver-manager
    opencv-python
    numpy
    pyautogui
    pillow
    openpyxl
    plyer
    python-dotenv
    requests
    """).strip()

FILES["README.md"] = textwrap.dedent("""\
    # Zimeitiboot - Self Media Automation (Bootstrap)
    This bootstrap creates the base project structure for the self-media automation tool.
    Files generated:
    - core/storage.py
    - core/plugin.py
    - core/plugin_loader.py
    - core/executor.py
    - platforms/mock_plugin.py
    - config/plugins.json
    - main_app.py (minimal test runner)
    - requirements.txt
    Usage:
    1. Run `python bootstrap_project.py` in an empty project folder.
    2. Activate your venv, install dependencies: `pip install -r requirements.txt`
    3. Run: `python main_app.py` to test DB + mock plugin execution.
    """)

# create directories and files
def ensure_path(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def write_file(p: Path, content: str):
    ensure_path(p)
    p.write_text(content, encoding='utf-8')
    print(f"wrote: {p}")

def main():
    print("Creating project structure under:", ROOT)
    # create dirs
    for d in ["config", "core", "platforms", "data", "utils", "tasks"]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
        print("mkdir:", ROOT / d)
    # write files
    for rel, content in FILES.items():
        p = ROOT / rel
        write_file(p, content)
    # also create example tasks/images dir and sample image placeholder text
    (ROOT / "tasks" / "images").mkdir(parents=True, exist_ok=True)
    sample_image_note = ROOT / "tasks" / "images" / "README.txt"
    sample_image_note.write_text("Place your media files (png/jpg/mp4) here for tasks.\n", encoding='utf-8')
    print("Bootstrap complete.")
    print("Next steps:")
    print("  1) activate your venv")
    print("  2) pip install -r requirements.txt")
    print("  3) python main_app.py")

if __name__ == "__main__":
    main()
