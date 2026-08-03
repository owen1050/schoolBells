import sqlite3, os, shutil
from datetime import date

DB_FILE = 'prod.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_FILE):
        shutil.copy2(DB_FILE, "backup.db")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS schools (id INTEGER PRIMARY KEY, name TEXT, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY, school_id INTEGER, name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS periods (id INTEGER PRIMARY KEY, schedule_id INTEGER, name TEXT, start_time TEXT, end_time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_schedules (school_id INTEGER, date TEXT, schedule_id INTEGER, PRIMARY KEY(school_id, date))''')
        conn.commit()

def get_all_schools():
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT id, name FROM schools').fetchall()]

def verify_admin(school_id, password):
    with get_connection() as conn:
        school = conn.execute('SELECT * FROM schools WHERE id = ? AND password = ?', (school_id, password)).fetchone()
        return school is not None

def get_todays_schedule(school_id):
    today_str = date.today().isoformat()
    with get_connection() as conn:
        # Check if there's a specific schedule set for today
        active = conn.execute('SELECT schedule_id FROM active_schedules WHERE school_id = ? AND date = ?', (school_id, today_str)).fetchone()
        
        if not active:
            # Fallback to the first schedule (usually "Regular") if none is explicitly set
            active = conn.execute('SELECT id as schedule_id FROM schedules WHERE school_id = ? LIMIT 1', (school_id,)).fetchone()
            if not active:
                return None
        
        schedule_id = active['schedule_id']
        schedule_info = conn.execute('SELECT name FROM schedules WHERE id = ?', (schedule_id,)).fetchone()
        periods = conn.execute('SELECT name, start_time, end_time FROM periods WHERE schedule_id = ? ORDER BY start_time', (schedule_id,)).fetchall()
        
        return {
            "schedule_name": schedule_info['name'],
            "periods": [dict(p) for p in periods]
        }

def get_school_schedules(school_id):
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT id, name FROM schedules WHERE school_id = ?', (school_id,)).fetchall()]

def create_schedule(school_id, name):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO schedules (school_id, name) VALUES (?, ?)', (school_id, name))
        return c.lastrowid

def set_todays_schedule(school_id, schedule_id):
    today_str = date.today().isoformat()
    with get_connection() as conn:
        conn.execute('REPLACE INTO active_schedules (school_id, date, schedule_id) VALUES (?, ?, ?)', (school_id, today_str, schedule_id))

def update_schedule_periods(schedule_id, periods_list):
    with get_connection() as conn:
        c = conn.cursor()
        # Clear out old periods for this schedule to avoid duplicates
        c.execute('DELETE FROM periods WHERE schedule_id = ?', (schedule_id,))
        
        # Insert the new periods
        for i in range(len(periods_list)):
            name = periods_list[i]['name']
            start_time = periods_list[i]['start_time']
            
            # The end time is the start time of the next period. 
            # If it's the last period, we leave the end time blank.
            end_time = periods_list[i+1]['start_time'] if i + 1 < len(periods_list) else ""
            
            c.execute('''INSERT INTO periods (schedule_id, name, start_time, end_time) 
                         VALUES (?, ?, ?, ?)''', (schedule_id, name, start_time, end_time))
        conn.commit()

def get_schedule_periods(schedule_id):
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT name, start_time FROM periods WHERE schedule_id = ? ORDER BY start_time',
            (schedule_id,)
        ).fetchall()
        return [dict(r) for r in rows]

