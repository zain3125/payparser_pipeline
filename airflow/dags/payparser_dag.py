# dags/payparser_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from sensors.image_sensor import NewImageSensor

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# إضافة مسار app/
sys.path.append('/opt/airflow/app')

from ocr import extract_text_from_image
from parser import parse_transaction_details_instapay, parse_transaction_details_cash
from db import insert_transaction
from utils import extract_receiver_name_from_filename

default_args = {
    'owner': 'zain',
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='payparser_pipeline_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # manual trigger
    catchup=False,
) as dag:

    wait_for_image = NewImageSensor(
        task_id='wait_for_new_image',
        folder_path='/opt/airflow/shared/downloads'
    )

    def do_ocr(ti):
        image_path = ti.xcom_pull(task_ids='wait_for_new_image', key='image_path')
        text = extract_text_from_image(image_path)
        ti.xcom_push(key='ocr_text', value=text)
        ti.xcom_push(key='image_path', value=image_path)

    ocr_task = PythonOperator(
        task_id='perform_ocr',
        python_callable=do_ocr
    )

    def do_parse(ti):
        text = ti.xcom_pull(task_ids='perform_ocr', key='ocr_text')
        image_path = ti.xcom_pull(task_ids='perform_ocr', key='image_path')
        if "EGP" in text:
            result = parse_transaction_details_instapay(text)
        else:
            result = parse_transaction_details_cash(text, image_path)
        ti.xcom_push(key='parsed_data', value=result)

    parse_task = PythonOperator(
        task_id='parse_transaction',
        python_callable=do_parse
    )

    def do_save(ti):
        parsed_data = ti.xcom_pull(task_ids='parse_transaction', key='parsed_data')
        image_path = ti.xcom_pull(task_ids='perform_ocr', key='image_path')
        filename = os.path.basename(image_path)
        receiver_name = extract_receiver_name_from_filename(filename)

        amount, sender, phone_number, date, transaction_id, status = parsed_data
        if all([amount, sender, date]):
            insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status)

    save_task = PythonOperator(
        task_id='save_transaction',
        python_callable=do_save
    )

    wait_for_image >> ocr_task >> parse_task >> save_task
