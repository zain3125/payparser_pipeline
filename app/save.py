from datetime import datetime
import os
import sqlite3
import pandas as pd
from app.app_config import DB_NAME, SAVEING_PATH

LAST_ID_FILE = os.path.join(SAVEING_PATH, 'last_id.txt')

def export_to_excel():
    try:
        os.makedirs(SAVEING_PATH, exist_ok=True)

        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, 'r') as f:
                last_id = int(f.read().strip() or 0)
        else:
            last_id = 0

        conn = sqlite3.connect(DB_NAME)
        query = f"""
        SELECT 
        t.id AS transaction_id,
        t.date,
        s.username AS sender_username,
        b.bank_name,
        t.receiver,
        t.phone_number,
        t.amount,
        t.transaction_id,
        t.status
    FROM transactions t
    JOIN senders s ON t.sender = s.id
    LEFT JOIN bank_name b ON s.id = b.id
    ORDER BY t.date DESC
    WHERE t.id > {last_id}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return

        file_name = f"Transactions data {datetime.now().strftime('%d %B %Y')}.xlsx"
        file_path = os.path.join(SAVEING_PATH, file_name)

        df.to_excel(file_path, index=False)

        new_last_id = df['id'].max()
        with open(LAST_ID_FILE, 'w') as f:
            f.write(str(new_last_id))

    except Exception as e:
        print(f"Failed to save:\n{e}")
