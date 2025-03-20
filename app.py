import requests
import sqlite3
import re
import json
from datetime import datetime

# chat gpt learn me how to use APIs
OCR_API_URL = "https://api.ocr.space/parse/image"
OCR_API_KEY = "K86506114588957"

DB_NAME = "transactions.db"

receiver_name = input("Enter receiver naem: ")


def extract_text_from_image(image_path):

    with open(image_path, 'rb') as image_file:
        response = requests.post(
            OCR_API_URL,
            files={"file": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "eng",
                "scale": "true",
                "OCREngine": "2",
                "isOverlayRequired": "false"
            }
        )

    try:
        result = response.json()  # Turn respone to JSON
        if isinstance(result, dict) and not result.get("IsErroredOnProcessing", True):
            return result["ParsedResults"][0]["ParsedText"]
        else:
            print("Error 69")
            return None
    except json.JSONDecodeError:
        print("Error 70")
        return None



def parse_transaction_details(text):
    """GPT learn me how to make formula to detect inputs"""
    amount_match = re.search(r"([\d,]+)\s*EGP", text)
    amount = amount_match.group(1).replace(",", "") if amount_match else None

    sender_match = re.search(r"[a-zA-Z0-9._%+-]+@instapay", text)
    sender = sender_match.group(0) if sender_match else None

    phone_match = re.search(r"\b(010|011|012|015)\d{8}\b", text)
    phone_number = phone_match.group(0) if phone_match else None

    date_match = re.search(r"(\d{1,2})\s(\w+)\s(\d{4})\s(\d{1,2}:\d{2}\s(?:AM|PM))", text)

    if date_match:
        day, month, year, time = date_match.groups()
        date = f"{day} {month} {year} {time}"
        month_table = f"{month}_{year}"
    else:
        date = None
        month_table = "Unknown"

    return amount, sender, phone_number, date, month_table



def validate_table_name(name):
    return re.match(r"^[a-zA-Z0-9_]+$", name) is not None



def insert_transaction(db_name, month_table, amount, sender, receiver_name, phone_number, date):
    if not validate_table_name(month_table):
        print(f"Error 71")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{month_table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sender TEXT,
            receiver TEXT,
            phone_number TEXT,
            amount INTEGER
        )
        """)

        cursor.execute(f"""
        INSERT INTO "{month_table}" (date, sender, receiver, phone_number, amount)
        VALUES (?, ?, ?, ?, ?)
        """, (date, sender, receiver_name, phone_number, amount))

        conn.commit()
        print(f"inserted to: {month_table}")

    except sqlite3.Error:
        print("Error 72")

    finally:
        conn.close()


# my main
image_path = input("Enter photo path: ").strip()
text = extract_text_from_image(image_path)

if text:
    print("Extracted text:\n", text)

    amount, sender, phone_number, date, month_table = parse_transaction_details(text)

    if all([amount, sender, date]):
        print(f"Enterd data:")
        print(f"Amount: {amount} EGP")
        print(f"From: {sender}")
        print(f"To: {receiver_name}")
        print(f"phone_number: {phone_number}")
        print(f"Date: {date}")
        print(f"Saved in: {month_table}")

        insert_transaction(DB_NAME, month_table, amount, sender, receiver_name, phone_number, date)
    else:
        print("Error 73")
else:
    print("Error 74")