import os
from app.tasks.airflow_config import WATCH_FOLDER, PROCESSED_FILE

def detect_new_images(ti):
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    if not os.path.exists(PROCESSED_FILE):
        open(PROCESSED_FILE, 'w').close()

    with open(PROCESSED_FILE, 'r') as f:
        processed = set(f.read().splitlines())

    all_images = []
    # Walk through watch folder and collect all images
    for root, dirs, files in os.walk(WATCH_FOLDER):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(root, file)
                all_images.append(full_path)

    # Check for new images not in processed
    new_images = [f for f in all_images if os.path.basename(f) not in processed]

    if not new_images:
        return False

    # Push new images to XCom
    ti.xcom_push(key='new_images', value=new_images)
    return True