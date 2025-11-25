import time
import random

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorResponseException

from app.app_config import OCR_API_URL, OCR_API_KEY

client = ComputerVisionClient(OCR_API_URL, CognitiveServicesCredentials(OCR_API_KEY))

def extract_text_from_image(image_path, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            with open(image_path, "rb") as image_file:
                response = client.read_in_stream(image_file, raw=True)

            operation_location = response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            while True:
                result = client.get_read_result(operation_id)
                if result.status.lower() not in ['notstarted', 'running']:
                    break
                time.sleep(1)

            if result.status == 'succeeded':
                return "\n".join(
                    [line.text for read_result in result.analyze_result.read_results for line in read_result.lines]
                )
            else:
                print("⚠️ OCR failed: Azure did not succeed")
                return None

        except ComputerVisionErrorResponseException as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = (2 ** retries) + random.uniform(0, 1)
                print(f"⏳ Too many requests, retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"❌ Azure OCR API error: {e}")
                return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

    print("🚫 OCR failed after max retries")
    return None
