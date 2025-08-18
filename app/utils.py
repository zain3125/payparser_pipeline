import re
from dateutil import parser
import os
import pandas as pd
import psycopg2
from app.app_config import PG_PARAMS, SAVEING_PATH

def extract_receiver_name_from_filename(filename):
    match = re.search(r'\((.*?)\)', filename)
    return match.group(1) if match else "Unknown"

def format_date_for_sqlite(date_str):
    try:
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Invalid date string")

        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Date formatting error: {e} | Rejected date string: '{date_str}'")
        return None

def extract_egyptian_phone_number(text):
    match = re.search(r"\b(010|011|012|015)\d{8}\b", text)
    if match:
        return match.group(0)
    text_cleaned = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    match = re.search(r"\b(010|011|012|015)\d{8}\b", text_cleaned)
    return match.group(0) if match else None

def convert_arabic_month_to_english(month_ar):
    arabic_months = {
        "يناير": "January", "فبراير": "February", "مارس": "March",
        "أبريل": "April", "ابريل": "April", "مايو": "May",
        "يونيو": "June", "يوليو": "July", "أغسطس": "August",
        "اغسطس": "August", "سبتمبر": "September", "أكتوبر": "October",
        "اكتوبر": "October", "نوفمبر": "November", "ديسمبر": "December"
    }
    return arabic_months.get(month_ar, month_ar)

def extract_date(text, pattern, is_arabic=False):
    match = re.search(pattern, text)
    if not match:
        print("Date not matched in text, returning full text:")
        print("Rejected date string:", repr(text))
        return None

    if is_arabic:
        day, month_ar, time, year = match.groups()
        day = day.replace('.', '')
        month = convert_arabic_month_to_english(month_ar)
    else:
        day, month, year, time = match.groups()

    return f"{day} {month} {year} {time}"


def extract_amount(text, pattern):
    match = re.search(pattern, text)
    return match.group(1).replace(",", "") if match else None

def extract_transaction_id(text):
    match = re.search(r"\b(5\d{11})\b(?=\s*الرقم المرجعي)", text)
    if match:
        return match.group(1), "completed"
    match = re.search(r"الرقم المرجعي\s*[\n\r]*\s*\b(5\d{11})\b", text)
    if match:
        return match.group(1), "completed"
    match = re.search(r"الرقم المرجعي[\.:\s]*[\n\r]*\s*\b(5\d{11})\b", text)
    if match:
        return match.group(1), "completed"
    match = re.search(r"الرقم المرجعي[:\s]*NA", text)
    if match:
        return None, "pending.."
    return None, "completed"

def extract_egyptian_phone_number_cach(text, n):
    text_cleaned = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    matches = re.findall(r'(?:010|011|012|015)\d{8}', text_cleaned)
    if len(matches) >= 2:
        return matches[n] # 0 for sender & 1 for receiver
    else:
        return None

def export_transactions_to_excel(start, end):
    try:
        conn = psycopg2.connect(**PG_PARAMS)
        cur = conn.cursor()

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

        cur.execute(query, (start, end))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.close()

        if not rows:
            return None

        df = pd.DataFrame(rows, columns=columns)
        os.makedirs(SAVEING_PATH, exist_ok=True)
        file_path = os.path.join(SAVEING_PATH, f"Transactions {start} to {end}.xlsx")
        df.to_excel(file_path, index=False)
        return file_path
    except Exception as e:
        print(f"Export error: {e}")
        return None
