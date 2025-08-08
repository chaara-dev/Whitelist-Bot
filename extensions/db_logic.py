import sqlite3
import math
from datetime import datetime
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
            reminded_stage TEXT DEFAULT "none",
            application_at TIMESTAMP,
            decision_at TIMESTAMP,
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
        CREATE TABLE IF NOT EXISTS staff_stats (
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
    c.execute("INSERT OR REPLACE INTO applications (thread_id, user_id, status, created_at) VALUES (?, ?, ?, ?)",
            (thread_id, user_id, 'open', datetime.now()))
    conn.commit()
    conn.close()

def update_created_timestamp(thread_id, user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("UPDATE applications SET application_at = ? WHERE thread_id = ? AND user_id = ?", (datetime.now(), thread_id, user_id))
    conn.commit()
    conn.close()

def mark_application(thread_id, status, reviewer_id=None): # status: open | approved | denied | abandoned
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ?, decision_at = ?, reviewer_id = ? WHERE thread_id = ?",
            (status, datetime.now(), reviewer_id, thread_id))
    conn.commit()
    conn.close()

def has_open_application(user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("""--sql
        SELECT COUNT(*) FROM applications
        WHERE user_id = ? AND status IN ('open')
    """, (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_open_application_id(user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT thread_id FROM applications WHERE status = 'open' AND user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0]

def update_staff_stats(staff_id, stat_type): # stat_type: approved | denied
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute(f"""--sql
        INSERT INTO staff_stats (staff_id, {stat_type})
        VALUES (?, 1)
        ON CONFLICT(staff_id) DO UPDATE SET {stat_type} = {stat_type} + 1
    """, (staff_id,))
    conn.commit()
    conn.close()

def get_whitelist_stats():
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM applications")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE status = 'approved'")
    approved = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE status = 'denied'")
    denied = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM applications WHERE status = 'abandoned'")
    abandoned = c.fetchone()[0]

    c.execute("SELECT staff_id, approved, denied FROM staff_stats ORDER BY approved DESC, denied DESC")
    staff_rows = c.fetchall()

    c.execute("""--sql
        SELECT application_at, decision_at FROM applications
        WHERE status IN ('approved', 'denied') 
        AND created_at IS NOT NULL 
        AND application_at IS NOT NULL
    """)
    times = c.fetchall()
    conn.close()

    total_minutes = 0
    for application_at, decision_at in times:
        
        t1 = datetime.strptime(application_at, "%Y-%m-%d %H:%M:%S.%f")
        t2 = datetime.strptime(decision_at, "%Y-%m-%d %H:%M:%S.%f")
        total_minutes += (t2-t1).total_seconds() / 60

    hours = math.floor(total_minutes / 60)
    minutes = math.floor(total_minutes % 60)
    
    return total, approved, denied, hours, minutes, staff_rows, abandoned

def get_open_member_applications(user_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications WHERE status = 'open' AND user_id = ?", (user_id,))
    open_apps = c.fetchall()
    conn.close()
    return open_apps

def get_open_application_threads(thread_id):
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications WHERE status = 'open' AND thread_id = ?", (thread_id,))
    open_apps = c.fetchall()
    conn.close()
    return open_apps

def get_all_open_applications():
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM applications WHERE status = 'open'")
    open_apps = c.fetchall()
    conn.close()
    return open_apps

def mark_applicant_reminded(thread_id, reminded_stage): # stage: none | warning | final_warning | complete
    conn = sqlite3.connect("storage/database.db")
    c = conn.cursor()
    c.execute("UPDATE applications SET reminded_stage = ? WHERE thread_id = ?", (reminded_stage, thread_id))
    conn.commit()
    conn.close()

async def setup(bot):
    initialize_database()
    print("Extension:", colored("db_logic.py", "yellow"), "loaded.")