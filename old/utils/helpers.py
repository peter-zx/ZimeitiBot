# utils/helpers.py
import time
import random

def human_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """随机短暂停顿，模拟人操作节奏"""
    time.sleep(random.uniform(min_seconds, max_seconds))
