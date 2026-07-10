import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path


def init_db(path: str):
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS scrapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT, domain TEXT, mode TEXT, fmt TEXT,
        content TEXT, metadata TEXT, created_at TEXT)""")
    con.commit()
    con.close()


def save(path: str, url: str, domain: str, mode: str, fmt: str,
         content: str, metadata: dict):
    init_db(path)
    con = sqlite3.connect(path)
    con.execute(
        "INSERT INTO scrapes (url,domain,mode,fmt,content,metadata,created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (url, domain, mode, fmt, content,
         json.dumps(metadata, default=str), datetime.utcnow().isoformat()))
    con.commit()
    con.close()


def export_json(record: dict, out_path: str):
    Path(out_path).write_text(json.dumps(record, indent=2, default=str))


def export_csv(rows: list, out_path: str):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
