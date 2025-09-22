# utils/logger.py
import logging
import sys
from pathlib import Path

def get_logger(name: str = "app", log_file: str = None, level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(level)
        fh_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                                         datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

    return logger
