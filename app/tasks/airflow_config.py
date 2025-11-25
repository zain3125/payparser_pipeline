import os

# Configurations for Airflow tasks
WATCH_FOLDER = '/opt/airflow/shared/downloads'
TMP_FOLDER = '/opt/airflow/shared/tmp'
PROCESSED_FILE = '/opt/airflow/shared/processed_images.txt'
TMP_RESULT_FILE = os.path.join(TMP_FOLDER, 'classified_results.json')
