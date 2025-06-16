# dags/payparser_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow')
from app.tasks.detect import detect_new_images
from app.tasks.classify import ocr_and_classify
from app.tasks.rename import rename_images_by_transaction_id
from app.tasks.process import process_transactions


from app.parser import parse_transaction_details_instapay, parse_transaction_details_cash



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

    detect_task = ShortCircuitOperator(
        task_id='detect_new_images_task',
        python_callable=detect_new_images
    )

    classify_task = PythonOperator(
        task_id='ocr_and_classify_task',
        python_callable=ocr_and_classify,
        execution_timeout=timedelta(seconds=600)
    )

    instapay_task = PythonOperator(
        task_id='instapay_processing_task',
        python_callable=lambda ti: process_transactions(ti, 'instapay', parse_transaction_details_instapay)
    )

    cash_task = PythonOperator(
        task_id='cash_processing_task',
        python_callable=lambda ti: process_transactions(ti, 'cash', parse_transaction_details_cash)
    )

    rename_task = PythonOperator(
        task_id='rename_images_task',
        python_callable=rename_images_by_transaction_id
    )

    detect_task >> classify_task >> [instapay_task, cash_task] >> rename_task
