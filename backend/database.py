"""
数据库初始化 + 用户认证 + 吉他谱 CRUD
"""

import sqlite3
import hashlib
import hmac
import json
import time
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "guitartab.db")
SECRET = "guitartab-secret-key-2026"

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tabs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            tab_text TEXT NOT NULL,
            note_count INTEGER NOT NULL,
            mode TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()

def hash_password(password):
    return hashlib.sha256((password + SECRET).encode()).hexdigest()

def create_token(user_id):
    payload = json.dumps({"uid": user_id, "exp": int(time.time()) + 86400 * 7})
    sig = hmac.new(SECRET.encode(), payload.encode(), "sha256").hexdigest()
    return f"{payload}.{sig}"

def verify_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_str, sig = parts
        expected = hmac.new(SECRET.encode(), payload_str.encode(), "sha256").hexdigest()
        if sig != expected:
            return None
        payload = json.loads(payload_str)
        if payload["exp"] < time.time():
            return None
        return payload["uid"]
    except Exception:
        return None

init_db()
