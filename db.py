import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS chat_ids (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL
)
""")
cur.execute("ALTER TABLE chat_ids ADD COLUMN IF NOT EXISTS name TEXT DEFAULT 'Unknown'")

cur.execute("""
CREATE TABLE IF NOT EXISTS stock_cache (
    key TEXT PRIMARY KEY,
    data JSONB
)
""")

conn.commit()
cur.close()
conn.close()

def save_chat_id(chat_id, name="Unknown"):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_ids (chat_id, name) VALUES (%s, %s) ON CONFLICT (chat_id) DO UPDATE SET name = EXCLUDED.name", (chat_id, name))
    conn.commit()
    cur.close()
    conn.close()

def remove_chat_id(chat_id):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_ids WHERE chat_id = %s", (chat_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_chat_ids():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chat_ids")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in result]

def get_chat_names():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT chat_id, name FROM chat_ids")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def save_stock_data(key, data):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("INSERT INTO stock_cache (key, data) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data", (key, json.dumps(data)))
    conn.commit()
    cur.close()
    conn.close()

def load_stock_data(key):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT data FROM stock_cache WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None
