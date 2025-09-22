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
