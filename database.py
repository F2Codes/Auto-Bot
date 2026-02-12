import sqlite3

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    conn.close()
    return users
