import sqlite3
import datetime
from termcolor import colored

def initialize_database():
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("""--sql
        CREATE TABLE IF NOT EXISTS applications (
            thread_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            status TEXT,
            created_at TIMESTAMP,
            decision_at TIMESTAMP,
            applicant_reminded INTEGER DEFAULT 0,
            staff_reminded INTEGER DEFAULT 0,
            reviewer_id INTEGER
        )
    """)
    c.execute("""--sql
        CREATE TABLE IF NOT EXISTS embed_messages (
            embed_name TEXT PRIMARY KEY,
            message_id INTEGER
        )
    """)
    c.execute("""--sql
        CREATE TABLE IF NOT EXISTS app_stats (
            staff_id INTEGER PRIMARY KEY,
            approved INTEGER DEFAULT 0,
            denied INTEGER DEFAULT 0
        )

    """)
    conn.commit()
    conn.close()

def load_stored_id(embed_name):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT message_id FROM embed_messages WHERE embed_name = ?", (embed_name,))
    message_id = c.fetchone()
    conn.close()
    if message_id is not None:
        return message_id[0]
    else:
        return None

def store_id(embed_name, message_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("INSERT INTO embed_messages (embed_name, message_id) VALUES (?, ?) ON CONFLICT(embed_name) DO UPDATE SET message_id = ?", 
            (embed_name, message_id, message_id))
    conn.commit()
    conn.close()

def insert_application(thread_id, user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO applications (thread_id, user_id, status, created_at) VALUES (?, ?, ?, ?)",
            (thread_id, user_id, 'open', datetime.datetime.now()))
    conn.commit()
    conn.close()

def mark_application(thread_id, status, reviewer_id=None):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ?, decision_at = ?, reviewer_id = ? WHERE thread_id = ?",
            (status, datetime.datetime.now(), reviewer_id, thread_id))
    conn.commit()
    conn.close()

def has_open_application(user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM applications WHERE status = 'open' AND user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result is not None:
        return True
    else:
        return False

def get_open_application_id(user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT thread_id FROM applications WHERE status = 'open' AND user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0]


async def setup(bot):
    initialize_database()
    print("Extension:", colored("db_logic.py", "yellow"), "loaded.")