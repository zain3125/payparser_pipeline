import requests
import json
from config import OCR_API_URL, OCR_API_KEY

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_file:
        response = requests.post(
            OCR_API_URL,
            files={"file": image_file},
            data={
                "apikey": OCR_API_KEY,
                "language": "auto",
                "scale": "true",
                "OCREngine": "2",
                "isOverlayRequired": "false"
            }
        )
    try:
        result = response.json()
        if isinstance(result, dict) and not result.get("IsErroredOnProcessing", True):
            return result["ParsedResults"][0]["ParsedText"]
        else:
            print("Error: OCR processing failed.")
            return None
    except json.JSONDecodeError:
        print("Error: OCR JSON decode failed.")
        return None
