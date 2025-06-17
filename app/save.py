from datetime import datetime
import os
import sqlite3
import pandas as pd
from app.app_config import DB_NAME, SAVEING_PATH

LAST_ID_FILE = os.path.join(SAVEING_PATH, 'last_id.txt')

def export_to_csv():
    try:
        os.makedirs(SAVEING_PATH, exist_ok=True)

        if os.path.exists(LAST_ID_FILE):
            with open(LAST_ID_FILE, 'r') as f:
                last_id = int(f.read().strip() or 0)
        else:
            last_id = 0

        conn = sqlite3.connect(DB_NAME)

        query = f"SELECT * FROM transactions WHERE id > {last_id}"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("No new records found.")
            return

        file_name = f"Transactions data {datetime.now().strftime('%d %B %Y')}.csv"
        file_path = os.path.join(SAVEING_PATH, file_name)

        df.to_csv(file_path, index=False)
        print("Success", f"Data saved to {file_path}")

        new_last_id = df['id'].max()
        with open(LAST_ID_FILE, 'w') as f:
            f.write(str(new_last_id))

    except Exception as e:
        print("Error", f"Failed to save:\n{e}")
