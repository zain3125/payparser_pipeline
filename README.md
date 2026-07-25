# PayParser Pipeline

End-to-end transaction receipt processing pipeline that collects images from Telegram, extracts text via OCR, classifies and parses transaction details, and stores structured data in PostgreSQL — orchestrated by Apache Airflow.

## Overview

This project automates the extraction and organization of transaction data from receipt images shared in a Telegram group. Images are collected by a Telethon-based bot, then processed through an Airflow-orchestrated pipeline that performs OCR (Azure Computer Vision), classifies receipts as Instapay or Vodafone Cash, parses transaction details, and stores everything in a PostgreSQL database. Results can be exported to Excel via a Tkinter GUI.

The pipeline handles Arabic and English text, Egyptian phone numbers, Arabic-Indic numeral conversion, and multiple receipt formats.

## Architecture & Data Flow

```text
Telegram Group
      |
      v
telegram-listener/bot.py (Telethon)
      |
      v
airflow/shared/downloads/{sender}/
      |
      v
Airflow DAG (payparser_dag.py)
      |
      |-- detect_new_images (ShortCircuit)
      |         |
      |         v
      |-- ocr_and_classify
      |         |
      |         +-- Azure Computer Vision OCR
      |         +-- Classify: instapay vs cash
      |         |
      |         v
      |-- [instapay_processing]    (parallel)
      |     [cash_processing]      (parallel)
      |         |
      |         +-- Parse transaction details
      |         +-- Insert into PostgreSQL
      |         |
      |         v
      +-- rename_images
                |
                +-- Rename by transaction ID
                +-- Archive processed files
                |
                v
         PostgreSQL Database
                |
                v
      manual_save.py (Tkinter GUI)
                |
                v
         Excel Export
```

## Technologies Used

- **Python 3.12** — Core language for bot, tasks, and parsing logic
- **Telethon** — Telegram user client for reading group messages and downloading media
- **Apache Airflow 2.10.5** — Workflow orchestration (CeleryExecutor)
- **Docker** — Containerized Airflow deployment
- **PostgreSQL** — Transaction data storage
- **Azure Computer Vision** — OCR text extraction from receipt images
- **Pandas / openpyxl** — Excel export
- **Tkinter** — Manual export GUI
- **Requests** — Airflow REST API communication
- **python-dotenv** — Environment variable management

## Project Structure

```
payparser_pipeline/
├── .env                              # Global config (OCR, Postgres, paths)
├── .gitignore
├── README.md
│
├── telegram-listener/                # Image ingestion from Telegram
│   ├── .env                          # Telegram API_ID, API_HASH, GROUP_NAME
│   ├── bot.py                        # Telethon client, downloads today's photos
│   ├── config.py                     # Loads .env into constants
│   ├── requirements.txt              # telethon, python-dotenv
│   └── session/                      # Telethon session persistence
│
├── app/                              # Core processing logic
│   ├── app_config.py                 # Central config from .env
│   ├── ocr.py                        # Azure Computer Vision OCR client
│   ├── parser.py                     # Instapay & Cash receipt parsers
│   ├── utils.py                      # Phone, date, amount, ID extraction helpers
│   ├── db.py                         # PostgreSQL table creation + inserts
│   ├── manual_save.py                # Tkinter GUI for Excel export
│   └── tasks/                        # Airflow-callable task modules
│       ├── airflow_config.py         # Container-internal path constants
│       ├── detect.py                 # ShortCircuit: find new images
│       ├── classify.py               # OCR + classify (instapay/cash)
│       ├── process.py                # Parse + insert to database
│       └── rename.py                 # Rename by transaction ID + archive
│
└── airflow/                          # Dockerized Airflow environment
    ├── Dockerfile                    # apache/airflow:2.10.5 + custom deps
    ├── docker-compose.yaml           # Full CeleryExecutor cluster
    ├── requirements.txt              # Python deps for Airflow container
    ├── dags/
    │   └── payparser_dag.py          # DAG definition
    ├── shared/                       # Runtime: downloads, tmp, archives
    ├── config/                       # Airflow config overrides
    ├── plugins/                      # Airflow plugins
    ├── data_bases/                   # Legacy SQLite (unused)
    ├── Excell_sheets/                # Excel export output
    └── logs/                         # Airflow task logs
```

## Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL database (accessible at configured host/port)
- Azure Computer Vision resource (endpoint + API key)
- Telegram API credentials (from https://my.telegram.org)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/payparser_pipeline.git
cd payparser_pipeline
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
# Azure OCR
OCR_API_URL=https://your-resource.cognitiveservices.azure.com/
OCR_API_KEY=your_api_key

# PostgreSQL
PG_DBNAME=your_database
PG_USER=your_user
PG_PASSWORD=your_password
PG_HOST=your_host
PG_PORT=5432

# Airflow
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.
WATCH_FOLDER=airflow/shared/downloads
SAVEING_PATH=Excell_sheets
```

Create a `.env` file in `telegram-listener/`:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
GROUP_NAME=your_group_name
AUTHOR_NAMES={"sender_id":"Display Name"}
```

### 3. Set Airflow variables

Set these via the Airflow UI (http://localhost:8080) or API:

- `group_name` — Telegram group name to monitor
- `author_names` — JSON mapping sender IDs to display names

### 4. Start Airflow

```bash
cd airflow
docker-compose up airflow-init
docker-compose up -d
```

Access the Airflow UI at http://localhost:8080 (username: `airflow`, password: `airflow`).

### 5. Set up the Telegram bot

```bash
cd telegram-listener
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

On first run, you will be prompted for your Telegram phone number and verification code. The session is saved in `telegram-listener/session/` for subsequent runs.

## How to Run

### Automated (production)

1. Start Airflow: `cd airflow && docker-compose up -d`
2. Run the Telegram bot (manually or as a systemd service): `python telegram-listener/bot.py`
3. The Airflow DAG runs daily at 1:00 AM (Africa/Cairo timezone) and processes all new images

### Manual export

To export transactions to Excel:

```bash
cd app
python manual_save.py
```

A Tkinter GUI will appear. Select a date range and click "Export to Excel Sheet". The file is saved to `Excell_sheets/`.

## Pipeline Workflow

### Step 1: Image Collection (`telegram-listener/bot.py`)

- Connects to Telegram via Telethon user client
- Finds the configured group by name from Airflow variables
- Iterates over the last 500 messages
- Filters to today's date only
- Downloads only photo messages
- Saves images to `airflow/shared/downloads/{sender_name}/`
- Filenames follow the pattern: `photo_{timestamp}({caption}).jpg`

### Step 2: Image Detection (`app/tasks/detect.py`)

- Walks `airflow/shared/downloads/` for `.jpg`, `.jpeg`, `.png` files
- Pushes discovered file paths to XCom
- Returns `False` (short-circuits the entire pipeline) if no new images found

### Step 3: OCR & Classification (`app/tasks/classify.py`)

- Pulls image paths from XCom
- Sends each image to Azure Computer Vision Read API
- Classifies as `instapay` if OCR text contains "EGP", otherwise `cash`
- Saves results to `classified_results.json` and pushes to XCom
- Includes retry logic with exponential backoff for rate-limited OCR calls

### Step 4: Transaction Processing (`app/tasks/process.py`)

Runs in parallel for both receipt types:

- **Instapay**: Extracts amount, sender email, phone number, date, transaction ID, and status
- **Cash**: Extracts amount, date, transaction ID; handles Arabic-Indic numeral conversion; sender derived from folder name
- Inserts each transaction into PostgreSQL with duplicate detection (`ON CONFLICT DO NOTHING`)

### Step 5: Image Renaming & Archival (`app/tasks/rename.py`)

- Renames processed images to `{transaction_id}.{ext}` for traceability
- Moves all processed files to an archive folder: `shared/Transactions DD Month YYYY`

### Step 6: Export (optional)

- `app/manual_save.py` provides a Tkinter GUI to query PostgreSQL and export to Excel

## Database Schema

Three tables in PostgreSQL:

| Table | Columns | Purpose |
|-------|---------|---------|
| `senders` | `sender_id` (PK), `username` | Unique sender registry |
| `bank_name` | `bank_id` (PK, FK -> senders), `bank_name` | Bank type per sender |
| `transactions` | `internal_transaction_id` (PK), `date`, `sender` (FK), `receiver`, `phone_number`, `amount`, `transaction_id` (UNIQUE), `status` | All parsed transactions |

## Key Analyses

| Component | Description |
|-----------|-------------|
| OCR Extraction | Azure Computer Vision Read API with retry/backoff |
| Instapay Parsing | Regex-based extraction of amount, sender, phone, date, transaction ID, status |
| Cash Parsing | Arabic-Indic numeral conversion, Arabic month mapping, amount/date/ID extraction |
| Phone Detection | Egyptian phone number patterns (010/011/012/015 + 8 digits) |
| Sender Resolution | Maps Telegram sender IDs to display names via Airflow variables |
| Duplicate Prevention | PostgreSQL `ON CONFLICT (transaction_id) DO NOTHING` |

## Future Improvements

- Add real-time image processing (process images as they arrive, not just daily)
- Implement receipt validation before database insertion
- Add support for additional receipt types (e.g., bank transfers)
- Build a web dashboard for transaction monitoring
- Add automated testing for parser functions
- Implement CI/CD pipeline for deployment
- Add Databricks-compatible notebook versions for cloud deployment

## License

This project is for educational and portfolio purposes.
