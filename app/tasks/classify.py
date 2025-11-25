import os
import json
from app.tasks.airflow_config import TMP_FOLDER, TMP_RESULT_FILE
from app.ocr import extract_text_from_image

def ocr_and_classify(ti):
    os.makedirs(TMP_FOLDER, exist_ok=True)
    # Pull new images from XCom
    new_images = ti.xcom_pull(task_ids='detect_new_images_task', key='new_images')

    instapay_data = []
    cash_data = []

    for image_path in new_images:
        try:
            print(f"OCR processing: {image_path}")
            # Save extracted text from image to text
            text = extract_text_from_image(image_path)
            
            if not text:
                print("Warning: OCR returned None or empty text. Skipping.")
                continue
            
            # Classify transaction type
            tx_type = "instapay" if "EGP" in text else "cash"

            tx_data = {
                "text": text,
                "filename": image_path
            }

            # Save the text to a temporary dictionary
            if tx_type == "instapay":
                instapay_data.append(tx_data)
            else: # Cash
                cash_data.append(tx_data)

        except Exception as e:
            print(f"Error during OCR/classification: {e}")

    # Write in classified_results.json
    with open(TMP_RESULT_FILE, 'w') as f:
        json.dump({"instapay": instapay_data, "cash": cash_data}, f)

    # Calculate the number of transactions and their types
    with open(TMP_RESULT_FILE, 'r') as f:
        data = json.load(f)
    # Print the number of transactions and their types
    print(f"Found {len(data.get('instapay', []))} instapay & {len(data.get('cash', []))} cash transactions")

    ti.xcom_push(key='classified', value={"instapay": instapay_data, "cash": cash_data})
    ti.xcom_push(key='data', value=data)
