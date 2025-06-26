import sqlite3
from app.app_config import DB_NAME

def insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status):

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE DEFAULT (datetime('now', '+3 hours')),
    sender TEXT,
    receiver TEXT,
    phone_number TEXT,
    amount INTEGER,
    transaction_id TEXT UNIQUE,
    status TEXT DEFAULT 'completed'
        )
        """)

        if date:
            cursor.execute("""
            INSERT INTO "transactions" (date, sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, sender, receiver_name, phone_number, amount, transaction_id if transaction_id else None, status))
        else:
            cursor.execute("""
            INSERT INTO "transactions" (sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (sender, receiver_name, phone_number, amount, transaction_id if transaction_id else None, status))

        conn.commit()
        print(f"Inserted transaction into table: transactions")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()