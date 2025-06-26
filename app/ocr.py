from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from app.app_config import OCR_API_URL, OCR_API_KEY
import time

client = ComputerVisionClient(OCR_API_URL, CognitiveServicesCredentials(OCR_API_KEY))

def extract_text_from_image(image_path):
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
            text = "\n".join(
                [line.text for read_result in result.analyze_result.read_results for line in read_result.lines]
            )
            return text
        else:
            print("OCR failed: Azure did not succeed")
            return None

    except Exception as e:
        print(f"Azure OCR error: {e}")
        return None
