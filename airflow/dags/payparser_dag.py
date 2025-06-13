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
from utils import extract_receiver_name_from_filename

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
                print(f"🔍 OCR processing: {image_path}")
                text = extract_text_from_image(image_path)

                if "EGP" in text:
                    result = parse_transaction_details_instapay(text)
                    tx_type = "instapay"
                else:
                    result = parse_transaction_details_cash(text, image_path)
                    tx_type = "cash"

                amount, sender, phone_number, date, transaction_id, status = result
                receiver_name = extract_receiver_name_from_filename(os.path.basename(image_path))

                tx_data = {
                    "amount": amount,
                    "sender": sender,
                    "receiver_name": receiver_name,
                    "phone_number": phone_number,
                    "date": date,
                    "transaction_id": transaction_id,
                    "status": status,
                    "filename": os.path.basename(image_path)
                }

                if tx_type == "instapay":
                    instapay_data.append(tx_data)
                else:
                    cash_data.append(tx_data)

            except Exception as e:
                print(f"❌ Error during OCR/classification: {e}")

        with open(TMP_RESULT_FILE, 'w') as f:
            json.dump({"instapay": instapay_data, "cash": cash_data}, f)
        
        ti.xcom_push(key='classified', value={"instapay": instapay_data, "cash": cash_data})

    classify_task = PythonOperator(
        task_id='ocr_and_classify_task',
        python_callable=ocr_and_classify
    )

    def process_instapay(ti):
        classified = ti.xcom_pull(task_ids='ocr_and_classify_task', key='classified')
        if not classified:
            print("⚠️ No classified data found for instapay.")
            return

        instapay_images = classified.get('instapay', [])

        for tx in instapay_images:
            try:
                tx.pop('filename', None)
                insert_transaction(**tx)
                print(f"✅ Instapay transaction inserted: {tx}")
            except Exception as e:
                print(f"❌ Failed to insert instapay transaction: {e}")



    instapay_task = PythonOperator(
        task_id='instapay_processing_task',
        python_callable=process_instapay
    )

    def process_cash(ti):
        classified = ti.xcom_pull(task_ids='ocr_and_classify_task', key='classified')
        if not classified:
            print("⚠️ No classified data found for cash.")
            return

        cash_images = classified.get('cash', [])

        for tx in cash_images:
            try:
                tx.pop('filename', None)
                insert_transaction(**tx)
                print(f"✅ Cash transaction inserted: {tx}")
            except Exception as e:
                print(f"❌ Failed to insert cash transaction: {e}")


    cash_task = PythonOperator(
        task_id='cash_processing_task',
        python_callable=process_cash
        )

    detect_task >> classify_task >> [instapay_task, cash_task]
