import os
import psycopg2
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
conn.commit()
cur.close()
conn.close()

def save_chat_id(chat_id):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_ids (chat_id) VALUES (%s) ON CONFLICT DO NOTHING", (chat_id,))
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
