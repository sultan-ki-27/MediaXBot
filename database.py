import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    downloads INTEGER DEFAULT 0
)
""")
conn.commit()

def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def increase(user_id):
    cur.execute("UPDATE users SET downloads = downloads + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def get_stats(user_id):
    cur.execute("SELECT downloads FROM users WHERE user_id = ?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else 0
