import sqlite3
from app.app_config import DB_NAME

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS senders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bank_name (
        id INTEGER PRIMARY KEY,
        bank_name TEXT,
        FOREIGN KEY (id) REFERENCES senders(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT DEFAULT (datetime('now', '+3 hours')),
        sender INTEGER,
        receiver TEXT,
        phone_number TEXT,
        amount INTEGER,
        transaction_id TEXT UNIQUE,
        status TEXT DEFAULT 'completed',
        FOREIGN KEY (sender) REFERENCES senders(id)
    )
    """)

def get_or_create_sender(cursor, username):
    if not username:
        return None
    cursor.execute("SELECT id FROM senders WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO senders (username) VALUES (?)", (username,))
    return cursor.lastrowid

def insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Ensure tables exist
        create_tables(cursor)

        # Insert or get sender
        sender_id = get_or_create_sender(cursor, sender)

        # Prepare insert statement
        if date:
            query = """
            INSERT OR IGNORE INTO transactions 
            (date, sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                date, sender_id, receiver_name, phone_number, amount,
                transaction_id if transaction_id else None,
                status
            ))
        else:
            query = """
            INSERT OR IGNORE INTO transactions 
            (sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                sender_id, receiver_name, phone_number, amount,
                transaction_id if transaction_id else None,
                status
            ))

        conn.commit()
        print("Inserted transaction into table: transactions")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()
