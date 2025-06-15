# dags/payparser_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta
import os
import json
import sys

sys.path.append('/opt/airflow/app')

from ocr import extract_text_from_image
from parser import parse_transaction_details_instapay, parse_transaction_details_cash
from db import insert_transaction
from utils import extract_receiver_name_from_filename, extract_transaction_id

WATCH_FOLDER = '/opt/airflow/shared/downloads'
TMP_FOLDER = '/opt/airflow/shared/tmp'
PROCESSED_FILE = '/opt/airflow/shared/processed_images.txt'
TMP_RESULT_FILE = os.path.join(TMP_FOLDER, 'classified_results.json')

default_args = {
    'owner': 'zain',
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='payparser_pipeline_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 1 * * *',
    catchup=False,
) as dag:

    def detect_new_images(ti):
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        if not os.path.exists(PROCESSED_FILE):
            open(PROCESSED_FILE, 'w').close()

        with open(PROCESSED_FILE, 'r') as f:
            processed = set(f.read().splitlines())

        all_images = []
        for root, dirs, files in os.walk(WATCH_FOLDER):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    full_path = os.path.join(root, file)
                    all_images.append(full_path)

        new_images = [f for f in all_images if os.path.basename(f) not in processed]

        if not new_images:
            return False

        ti.xcom_push(key='new_images', value=new_images)
        return True

    detect_task = ShortCircuitOperator(
        task_id='detect_new_images_task',
        python_callable=detect_new_images
    )

    def ocr_and_classify(ti):
        os.makedirs(TMP_FOLDER, exist_ok=True)
        new_images = ti.xcom_pull(task_ids='detect_new_images_task', key='new_images')

        instapay_data = []
        cash_data = []

        for image_path in new_images:
            try:
                print(f"OCR processing: {image_path}")
                text = extract_text_from_image(image_path)

                tx_type = "instapay" if "EGP" in text else "cash"

                tx_data = {
                    "text": text,
                    "filename": image_path
                }

                if tx_type == "instapay":
                    instapay_data.append(tx_data)
                else:
                    cash_data.append(tx_data)

            except Exception as e:
                print(f"Error during OCR/classification: {e}")

        with open(TMP_RESULT_FILE, 'w') as f:
            json.dump({"instapay": instapay_data, "cash": cash_data}, f)

        ti.xcom_push(key='classified', value={"instapay": instapay_data, "cash": cash_data})

    classify_task = PythonOperator(
        task_id='ocr_and_classify_task',
        python_callable=ocr_and_classify
    )

    def rename_images_by_transaction_id(ti):
        print("Starting rename task...")

        if not os.path.exists(TMP_RESULT_FILE):
            print("TMP_RESULT_FILE not found:", TMP_RESULT_FILE)
            return

        with open(TMP_RESULT_FILE, 'r') as f:
            data = json.load(f)

        if not data:
            print("No data found in TMP_RESULT_FILE.")
            return

        print(f"Found {len(data.get('instapay', []))} instapay & {len(data.get('cash', []))} cash transactions")

        for tx_type in ['instapay', 'cash']:
            for tx in data.get(tx_type, []):
                print(f"Processing: {tx}")
                text = tx.get("text", "")
                fname = tx.get("filename")

                if tx_type == "cash":
                    try:
                        _, _, _, _, txid, _ = parse_transaction_details_cash(text, fname)
                    except Exception as e:
                        print(f"Error extracting txid from cash: {e}")
                        txid = None
                else:
                    txid, _ = extract_transaction_id(text)

                if not txid or not fname:
                    print(f"Skipping: missing txid or filename: {tx}")
                    continue

                found = False
                for root, dirs, files in os.walk(WATCH_FOLDER):
                    if fname in files:
                        src = os.path.join(root, fname)
                        ext = os.path.splitext(fname)[1]
                        dst = os.path.join(root, f"{txid}{ext}")
                        found = True

                        print(f"Rename {src} -> {dst}")

                        try:
                            os.rename(src, dst)
                            print(f"Renamed: {fname} -> {txid}{ext}")

                            with open(PROCESSED_FILE, 'a') as f:
                                f.write(os.path.basename(dst) + '\n')

                        except Exception as e:
                            print(f"Error renaming file: {e}")
                        break

                if not found:
                    print(f"Source file not found: {fname}")

    rename_task = PythonOperator(
        task_id='rename_images_task',
        python_callable=rename_images_by_transaction_id
    )

    def process_transactions(ti, tx_type, parser_function):
        classified = ti.xcom_pull(task_ids='ocr_and_classify_task', key='classified')
        if not classified:
            print(f"No classified data found for {tx_type}.")
            return

        transactions = classified.get(tx_type, [])

        for tx in transactions:
            try:
                text = tx.get("text", "")
                filename = tx.get("filename", "")

                if tx_type == "instapay":
                    amount, sender, phone_number, date, transaction_id, status = parser_function(text)
                    receiver_name = extract_receiver_name_from_filename(filename)
                else:
                    amount, sender, phone_number, date, transaction_id, status = parser_function(text, filename)
                    receiver_name = extract_receiver_name_from_filename(filename)

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


    instapay_task = PythonOperator(
        task_id='instapay_processing_task',
        python_callable=lambda ti: process_transactions(ti, 'instapay', parse_transaction_details_instapay)
    )

    cash_task = PythonOperator(
        task_id='cash_processing_task',
        python_callable=lambda ti: process_transactions(ti, 'cash', parse_transaction_details_cash)
    )

    detect_task >> classify_task >> rename_task >> [instapay_task, cash_task]
