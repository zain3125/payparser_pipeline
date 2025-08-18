import os
import psycopg2
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app_config import PG_PARAMS, SAVEING_PATH

# Create date choices
days = [f"{i:02}" for i in range(1, 32)]
months = [f"{i:02}" for i in range(1, 13)]
years = [str(y) for y in range(2020, datetime.now().year + 1)]

def get_selected_date(day_cb, month_cb, year_cb):
    return f"{year_cb.get()}-{month_cb.get()}-{day_cb.get()}"

# Date selector function
def create_date_selector(parent, default_day="01", default_month="01", default_year=years[-1]):
    frame = ttk.Frame(parent)
    day_cb = ttk.Combobox(frame, values=days, width=5)
    day_cb.set(default_day)
    day_cb.pack(side=tk.LEFT)

    month_cb = ttk.Combobox(frame, values=months, width=5)
    month_cb.set(default_month)
    month_cb.pack(side=tk.LEFT, padx=5)

    year_cb = ttk.Combobox(frame, values=years, width=7)
    year_cb.set(default_year)
    year_cb.pack(side=tk.LEFT)

    frame.pack()
    return day_cb, month_cb, year_cb

# Main function
def export_to_excel():
    start = get_selected_date(start_day, start_month, start_year)
    end = get_selected_date(end_day, end_month, end_year)

    if not start or not end:
        messagebox.showerror("Error", "Choose start and end date")
        return

    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cursor = conn.cursor()

        query = """
        SELECT 
            t.date,
            b.bank_name,
            t.receiver,
            t.phone_number,
            t.amount,
            t.transaction_id,
            t.status
        FROM transactions t
        JOIN senders s ON t.sender = s.sender_id
        LEFT JOIN bank_name b ON s.sender_id = b.bank_id
        WHERE t.date BETWEEN %s AND %s
        ORDER BY t.date DESC;
        """

        cursor.execute(query, (start, end))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("No Data", "No transactions found for selected date range.")
            return

        df = pd.DataFrame(rows, columns=columns)

        file_name = f"Transactions from {start} to {end}.xlsx"
        os.makedirs(SAVEING_PATH, exist_ok=True)
        file_path = os.path.join(SAVEING_PATH, file_name)

        df.to_excel(file_path, index=False)
        messagebox.showinfo("Saved", f"Successfully saved in:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save:\n{e}")

# GUI setup
root = tk.Tk()
root.title("Export transactions to Excel")
root.geometry("400x300")

# Choose start date
ttk.Label(root, text="Start date:").pack(pady=5)
start_day, start_month, start_year = create_date_selector(root)

# Choose end date
ttk.Label(root, text="End date:").pack(pady=5)
end_day, end_month, end_year = create_date_selector(root)

# Export button
ttk.Button(root, text="Export to Excel sheet", command=export_to_excel).pack(pady=20)

root.mainloop()
