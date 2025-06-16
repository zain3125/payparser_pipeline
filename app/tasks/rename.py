import os
from app.tasks.airflow_config import WATCH_FOLDER, PROCESSED_FILE
from app.parser import parse_transaction_details_cash
from app.utils import extract_transaction_id

def rename_images_by_transaction_id(ti):

    data = ti.xcom_pull(task_ids='ocr_and_classify_task', key='data')

    for tx_type in ['instapay', 'cash']:
        # Extract data for each transaction type
        for tx in data.get(tx_type, []):
            print(f"Processing: {tx}")
            text = tx.get("text", "")
            fname = tx.get("filename")

            # Extract from full function on parser.py
            if tx_type == "cash":
                try:
                    _, _, _, _, txid, _ = parse_transaction_details_cash(text, fname)
                except Exception as e:
                    print(f"Error extracting txid from cash: {e}")
                    txid = None
            # Dirctly extract from utils.py
            else:   # Instapay
                txid, _ = extract_transaction_id(text)

            if not txid or not fname:
                print(f"Skipping: missing txid or filename: {tx}")
                continue

            found = False
            # Search for file in WATCH_FOLDER
            for root, dirs, files in os.walk(WATCH_FOLDER):
                if os.path.basename(fname) in files:
                    src = os.path.join(root, os.path.basename(fname))
                    ext = os.path.splitext(fname)[1]
                    dst = os.path.join(root, f"{txid}{ext}")
                    found = True

                    try:
                        os.rename(src, dst)
                        print(f"Renamed: {fname} -> {txid}{ext}")

                        # Append to processed file
                        with open(PROCESSED_FILE, 'a') as f:
                            f.write(os.path.basename(dst) + '\n')

                    except Exception as e:
                        print(f"Error renaming file: {e}")
                    break

            if not found:
                print(f"Source file not found: {fname}")