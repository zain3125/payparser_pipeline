import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OCR_API_URL = os.getenv("OCR_API_URL")
OCR_API_KEY = os.getenv("OCR_API_KEY")

DB_NAME = os.path.join(BASE_DIR, '..', os.getenv("DB_NAME", "data_bases/system_data.db"))
WATCH_FOLDER = os.path.join(BASE_DIR, '..', os.getenv("WATCH_FOLDER", "whatsapp-bot/downloads"))
SAVEING_PATH = os.path.join(BASE_DIR, '..', os.getenv("SAVEING_PATH", "Excell_sheets"))
