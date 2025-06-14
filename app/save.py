import os
import sqlite3
import pandas as pd
from tkinter import ttk, messagebox, tk
from config import DB_NAME, SAVEING_PATH

def export_to_excel():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()

        file_name = f"Transactions data.xlsx"

        os.makedirs(SAVEING_PATH, exist_ok=True)

        file_path = os.path.join(SAVEING_PATH, file_name)

        df.to_excel(file_path, index=False)
        messagebox.showinfo("Saved", f"Saved correctly in\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save:\n{e}")

# GUI setup
root = tk.Tk()
root.title("Export to Excel")
root.geometry("300x150")

btn_export = ttk.Button(root, text="Export to Excel Sheet", command=export_to_excel)
btn_export.pack(pady=50)

root.mainloop()
