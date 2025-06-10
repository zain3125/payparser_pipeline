import re
from datetime import datetime

def extract_receiver_name_from_filename(filename):
    match = re.search(r'\((.*?)\)', filename)
    return match.group(1) if match else "Unknown"

def format_date_for_sqlite(date_str):
    try:
        if "AM" in date_str or "PM" in date_str:
            dt = datetime.strptime(date_str, "%d %B %Y %I:%M %p")
        else:
            dt = datetime.strptime(date_str, "%d %B %Y %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        print("Date formatting error:", e)
        return date_str


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
        return None
    if is_arabic:
        day, month_ar, time, year = match.groups()
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