import requests
import json
from app.app_config import OCR_API_URL, OCR_API_KEY

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
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, dict) and not result.get("IsErroredOnProcessing", True):
            return result["ParsedResults"][0]["ParsedText"]
        else:
            print(f"OCR error details: {result.get('ErrorMessage')}")
            print("Error: OCR processing failed (API returned error).")
            return None

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None

    except json.JSONDecodeError:
        print("Error: OCR JSON decode failed.")
        return None
