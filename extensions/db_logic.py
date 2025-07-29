import sqlite3
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


async def setup(bot):
    initialize_database()
    print("Extension:", colored("db_logic.py", "yellow"), "loaded.")