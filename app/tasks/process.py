from app.utils import extract_receiver_name_from_filename
from app.db import insert_transaction

def process_transactions(ti, tx_type, parser_function):
    print("Running processing...")
    classified = ti.xcom_pull(task_ids='ocr_and_classify_task', key='classified')
    if not classified:
        print(f"No classified data found for {tx_type}.")
        return

    transactions = classified.get(tx_type, [])
    for tx in transactions:
        try:
            text = tx.get("text", "")
            filename = tx.get("filename", "")
            receiver_name = extract_receiver_name_from_filename(filename)

            if tx_type == "instapay":
                amount, sender, phone_number, date, transaction_id, status = parser_function(text)
            else:
                amount, sender, phone_number, date, transaction_id, status = parser_function(text, filename)

            tx_data = {
                "amount": amount,
                "sender": sender,
                "receiver_name": receiver_name,
                "phone_number": phone_number,
                "date": date,
                "transaction_id": transaction_id,
                "status": status
            }

            insert_transaction(**tx_data)
            print(f"{tx_type.capitalize()} transaction inserted: {tx_data}")

        except Exception as e:
            print(f"Failed to insert {tx_type} transaction: {e}")
