# dags/payparser_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta
import os
import sys

# إضافة المسارات
sys.path.append('/opt/airflow/app')

from ocr import extract_text_from_image
from parser import parse_transaction_details_instapay, parse_transaction_details_cash
from db import insert_transaction
from utils import extract_receiver_name_from_filename

WATCH_FOLDER = '/opt/airflow/shared/downloads'
PROCESSED_FILE = '/opt/airflow/shared/processed_images.txt'

default_args = {
    'owner': 'zain',
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='payparser_pipeline_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 1 * * *',  # كل يوم الساعة 1 صباحًا
    catchup=False,
) as dag:

    def check_new_images(ti):
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        if not os.path.exists(PROCESSED_FILE):
            open(PROCESSED_FILE, 'w').close()

        with open(PROCESSED_FILE, 'r') as f:
            processed = set(f.read().splitlines())

        all_images = [f for f in os.listdir(WATCH_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        new_images = [f for f in all_images if f not in processed]

        if not new_images:
            return False

        ti.xcom_push(key='new_images', value=new_images)
        return True

    check_task = ShortCircuitOperator(
        task_id='check_for_new_images',
        python_callable=check_new_images
    )

    def process_images(ti):
        new_images = ti.xcom_pull(task_ids='check_for_new_images', key='new_images')
        for filename in new_images:
            image_path = os.path.join(WATCH_FOLDER, filename)
            print(f'⏳ Processing image: {image_path}')

            try:
                text = extract_text_from_image(image_path)

                if "EGP" in text:
                    result = parse_transaction_details_instapay(text)
                else:
                    result = parse_transaction_details_cash(text, image_path)

                amount, sender, phone_number, date, transaction_id, status = result
                receiver_name = extract_receiver_name_from_filename(filename)

                if all([amount, sender, date]):
                    insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status)
                    print(f'✅ Saved transaction for image: {filename}')
                else:
                    print(f'⚠️ Incomplete data for {filename}, skipped.')

            except Exception as e:
                print(f'❌ Error processing {filename}: {e}')

        # Mark all as processed
        with open(PROCESSED_FILE, 'a') as f:
            for filename in new_images:
                f.write(filename + '\n')

    process_task = PythonOperator(
        task_id='process_new_images',
        python_callable=process_images
    )

    check_task >> process_task
