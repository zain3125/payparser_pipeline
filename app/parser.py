import os
import re
from utils import extract_egyptian_phone_number, extract_date, extract_amount, extract_transaction_id, format_date_for_sqlite

def parse_transaction_details_instapay(text):
    amount = extract_amount(text, r"([\d,]+)\s*EGP")
    sender_match = re.search(r"[a-zA-Z0-9._%+-]+@instapay", text)
    sender = sender_match.group(0) if sender_match else None
    phone_number = extract_egyptian_phone_number(text)
    date = extract_date(text, r"(\d{1,2})\s(\w+)\s(\d{4})\s(\d{1,2}:\d{2}\s(?:AM|PM))")
    date = format_date_for_sqlite(date)
    transaction_id, status = extract_transaction_id(text)
    if "لقد تجاوزت الحد" in text:
        status = "failed..."
    return amount, sender, phone_number, date, transaction_id, status

def parse_transaction_details_cash(text, filename):
    text = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    amount = extract_amount(text, r"([\d,]+)\s*جنيه")
    phone_number = extract_egyptian_phone_number(text)
    date = extract_date(text, r"(\d{1,2})\s(\w+)\s(\d{1,2}:\d{2})\s?(\d{4})", is_arabic=True)
    date = format_date_for_sqlite(date)
    sender = os.path.basename(os.path.dirname(filename))
    match = re.search(r"\b(\d{12})\b", text)
    transaction_id = match.group(1) if match else None
    if transaction_id == phone_number:
        transaction_id = None
    return amount, sender, phone_number, date, transaction_id, "completed"
