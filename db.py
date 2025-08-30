# db.py
import sqlite3
from typing import Dict, Any, List

DB = "festival_log.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # Media table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS media (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      festival TEXT,
      region TEXT,
      language TEXT,
      media_type TEXT,  -- audio|video|image|text
      file_path TEXT,
      transcript TEXT,
      translation TEXT,
      ai_caption TEXT,
      tags TEXT,
      contributor TEXT,
      created_at TEXT,
      extra_json TEXT
    );
    """)
    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

# ---------------- MEDIA FUNCTIONS ----------------
def insert_item(item: Dict[str, Any]):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO media (title, festival, region, language, media_type, file_path,
         transcript, translation, ai_caption, tags, contributor, created_at, extra_json)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
    """, (item['title'], item['festival'], item['region'], item['language'],
          item['media_type'], item['file_path'], item.get('transcript'),
          item.get('translation'), item.get('ai_caption'), item.get('tags'),
          item.get('contributor'), item.get('extra_json')))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def query_items(filters: Dict[str,str], search: str = None) -> List[Dict]:
    conn = sqlite3.connect(DB)
    base = "SELECT * FROM media WHERE 1=1"
    params = []
    if filters.get("festival"):
        base += " AND festival = ?"; params.append(filters["festival"])
    if filters.get("language"):
        base += " AND language = ?"; params.append(filters["language"])
    if filters.get("media_type") and filters["media_type"]!="All":
        base += " AND media_type = ?"; params.append(filters["media_type"])
    if search:
        like = f"%{search}%"
        base += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(tags) LIKE LOWER(?))"
        params += [like, like]
    cur = conn.cursor()
    rows = cur.execute(base, params).fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

# ---------------- USER FUNCTIONS ----------------
def add_user(username: str, password: str) -> bool:
    """Register a new user. Returns True if success, False if user exists."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username: str, password: str) -> bool:
    """Check if username/password is correct."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return row is not None
