import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ocr import extract_text_from_image
from parser import parse_transaction_details_instapay, parse_transaction_details_cash
from db import insert_transaction
from utils import extract_receiver_name_from_filename
from config import WATCH_FOLDER

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            print(f"\nNew image detected: {event.src_path}")
            process_image(event.src_path)

def wait_for_file_ready(file_path, retries=10, delay=0.5):
    for _ in range(retries):
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
            return True
        except PermissionError:
            print(f"Waiting for file to be fully written: {file_path}")
            time.sleep(delay)
    return False

def process_image(image_path):

    if not wait_for_file_ready(image_path):
        print(f"Error: Failed to access file after several attempts: {image_path}")
        return

    filename = os.path.basename(image_path)
    receiver_name = extract_receiver_name_from_filename(filename)
    print(f"Processing: {filename} | Receiver: {receiver_name}")

    text = extract_text_from_image(image_path)
    if text:
        print("Extracted text:\n", text)
        if "EGP" in text:
            amount, sender, phone_number, date, transaction_id, status = parse_transaction_details_instapay(text)
        else:
            amount, sender, phone_number, date, transaction_id, status = parse_transaction_details_cash(text, image_path)

        if all([amount, sender, date]):
            print(f"Data extracted:")
            print(f"Amount: {amount} EGP")
            print(f"From: {sender}")
            print(f"To: {receiver_name}")
            print(f"Phone: {phone_number}")
            print(f"Date: {date}")
            print(f"transaction_id is: {transaction_id}")
            print(f"status is: {status}")

            insert_transaction(amount, sender, receiver_name, phone_number, date, transaction_id, status)

        else:
            print("Warning: Incomplete data, skipping.")
    else:
        print("Warning: OCR failed, skipping.")

def start_watching(folder_path):
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"Starting to watch folder: {folder_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching(WATCH_FOLDER)
