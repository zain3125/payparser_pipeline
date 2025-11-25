import os
from app.tasks.airflow_config import WATCH_FOLDER

def detect_new_images(ti):
    all_images = []

    for root, dirs, files in os.walk(WATCH_FOLDER):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(root, file)
                all_images.append(full_path)

    if not all_images:
        return False

    ti.xcom_push(key='new_images', value=all_images)
    return True
