import psycopg2
from app.app_config import PG_PARAMS

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS senders (
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
        date TIMESTAMP DEFAULT (NOW() + INTERVAL '3 hours'),
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
    cursor.execute("SELECT id FROM senders WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO senders (username) VALUES (%s) RETURNING id", (username,))
    return cursor.fetchone()[0]

def insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status):
    conn = None
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        # Ensure tables exist
        create_tables(cursor)

        # Insert or get sender
        sender_id = get_or_create_sender(cursor, sender)

        # Prepare insert statement
        if date:
            query = """
            INSERT INTO transactions 
            (date, sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO NOTHING
            """
            cursor.execute(query, (
                date, sender_id, receiver_name, phone_number, amount,
                transaction_id if transaction_id else None,
                status
            ))
        else:
            query = """
            INSERT INTO transactions 
            (sender, receiver, phone_number, amount, transaction_id, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO NOTHING
            """
            cursor.execute(query, (
                sender_id, receiver_name, phone_number, amount,
                transaction_id if transaction_id else None,
                status
            ))

        conn.commit()
        print("Inserted transaction into table: transactions")

    except psycopg2.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()
