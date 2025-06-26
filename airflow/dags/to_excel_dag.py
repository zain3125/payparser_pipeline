# dags/to_excel_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow')
from app.save import export_to_excel

default_args = {
    'owner': 'zain',
    'retries': 1,
    'retry_delay': timedelta(seconds=10),
}

with DAG(
    dag_id='to_excel_dag',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 2 * * *',
    catchup=False,
) as dag:
    
    save_to_excel_task = PythonOperator(
        task_id='save_to_excel_task',
        python_callable= export_to_excel
    )