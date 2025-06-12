# dags/sensors/image_sensor.py
import os
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

class NewImageSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, folder_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_path = folder_path

    def poke(self, context):
        self.log.info(f"Checking for new images in: {self.folder_path}")
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    full_path = os.path.join(root, file)
                    self.log.info(f"Found image: {full_path}")
                    context['ti'].xcom_push(key='image_path', value=full_path)
                    return True
        return False
