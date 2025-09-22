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
            print(f"load_plugins: failed to load {module_name}.{class_name}: {e}")
    return plugins
