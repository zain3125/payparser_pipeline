# 💸 PayParser Pipeline

A complete end-to-end pipeline for extracting, classifying, and storing transaction data from WhatsApp receipt images using OCR, with orchestration via Apache Airflow and WhatsApp integration via a Node.js bot.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [WhatsApp Bot Details](#whatsapp-bot-details)
- [Airflow DAG Logic](#airflow-dag-logic)
- [App Module Details](#app-module-details)
- [Exporting Data](#exporting-data)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🖼️ Overview

PayParser Pipeline automates the extraction and organization of transaction data from images of receipts (e.g., sent via WhatsApp). It uses a WhatsApp bot to collect images, OCR to extract text, Python logic to parse and classify transactions, and Airflow to orchestrate the workflow and store results in a PostgreSQL database.

---

## 🏗️ Architecture

```
WhatsApp Group
    │
    ▼
[whatsapp-bot (Node.js)]
    │
    ▼
airflow/shared/downloads/ (images)
    │
    ▼
[Airflow DAG]
    │
    ├─ OCR & Classification
    ├─ Image Renaming by Transaction ID
    └─ Database Insertion (PostgreSQL)
    │
    ▼
airflow/shared/tmp/classified_results.json
    │
    ▼
[Export to Excel (GUI)]
```

---

## 🚀 Features

- **WhatsApp Integration:** Downloads images from a specified WhatsApp group, organizes them by sender.
- **Automated Folder Monitoring:** Detects new images for processing.
- **OCR Extraction: Uses Azure AI Vision API for high-accuracy text extraction and receipt recognition.
- **Transaction Classification:** Distinguishes between Instapay and Vodafone Cash receipts.
- **Image Renaming:** Renames images by transaction ID for traceability.
- **Structured Data Storage:** Saves parsed data into a PostgreSQL database.
- **Airflow Orchestration:** Modular, scheduled, and visualized pipeline management.
- **Excel Export:** Export all transactions to Excel via a simple GUI.

---

## 📁 Folder Structure

```
payparser_pipeline/
├── airflow/
│   ├── config/
│   ├── dags/
│   │   ├── payparser_dag.py
│   │   └── to_csv_dag.py
│   ├── logs/
│   ├── plugins/
│   └── docker-compose.yaml
├── app/
│   ├── airflow_config.py
│   ├── classify.py
│   ├── detect.py
│   ├── process.py
│   ├── rename.py
│   ├── app_config.py
│   ├── db.py
│   ├── ocr.py
│   ├── parser.py
│   ├── save.py
│   ├── utils.py
│   └── tasks/
│	    ├── airflow_config.py
│   	├── classify.py
│   	├── detect.py
│   	├── process.py
│		└── rename.py
├── shared/
│   ├── downloads/
│   ├── tmp/
│   │   └── classified_results.json
│   └── processed_images.txt
├── data_bases/
│   └── system_data.db
├── Excell_sheets/
├── whatsapp-bot/
│   └── index.js
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚡ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/payparser_pipeline.git
cd payparser_pipeline
```

### 2. Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Node.js dependencies for WhatsApp bot

```bash
cd whatsapp-bot
npm install
cd ..
```

### 4. Airflow setup (Docker)

```bash
cd airflow
docker-compose up airflow-init
docker-compose up -d
```

### 5. Environment variables

Create a `.env` file in the project root with:

```env
AZURE_VISION_ENDPOINT=YOUR_AZURE_ENDPOINT
OCR_API_KEY=YOUR_OCR_API_KEY
DB_NAME=data_bases/system_data.db
WATCH_FOLDER=whatsapp-bot/downloads
SAVEING_PATH=Excell_sheets
AIRFLOW_PROJ_DIR=E:/python projects/payparser_pipeline
AIRFLOW_UID=50000
```

---

## ⚙️ Configuration

- **Airflow Variables:**  
  Set via Airflow UI or API:
  - `group_name`: WhatsApp group name to monitor.
  - `author_names`: JSON mapping WhatsApp IDs to readable names.

- **OCR API:**  
  Get your API key from Azure AI Vision (Azure Portal → Cognitive Services → Vision API).

---

## 🔄 How It Works

1. **Image Collection:**  
   The WhatsApp bot downloads images from the specified group and saves them in `shared/downloads/<author_name>/`.

2. **Airflow DAG:**  
   - Detects new images not yet processed.
   - Runs OCR and classifies each image as Instapay or Cash.
   - Renames images by transaction ID.
   - Parses transaction details and inserts them into the PostgreSQL database.

3. **Export:**  
   Use the GUI (`app/save.py`) to export all transactions to Excel.

---

## 🤖 WhatsApp Bot Details

- **Location:** [`whatsapp-bot/index.js`](whatsapp-bot/index.js)
- **Tech:** [venom-bot](https://github.com/orkestral/venom)
- **How it works:**
  - Connects to WhatsApp Web via QR code.
  - Downloads images from the configured group.
  - Organizes images by sender.
  - Reads group and author info from Airflow variables via REST API.

---

## 🌀 Airflow DAG Logic

- **File:** [`airflow/dags/payparser_dag.py`](airflow/dags/payparser_dag.py)
- **Main Tasks:**
  1. **detect_new_images:** Finds new images in `shared/downloads/`.
  2. **ocr_and_classify:** Runs OCR and classifies images.
  3. **rename_images_task:** Renames images by transaction ID.
  4. **instapay_processing_task / cash_processing_task:** Parses and inserts transaction data into the database.

---

## 🐍 App Module Details

- **OCR:** [`app/ocr.py`](app/ocr.py) — Calls OCR.Azure API.
- **Parsing:** [`app/parser.py`](app/parser.py) — Extracts transaction details.
- **Database:** [`app/db.py`](app/db.py) — Inserts transactions into PostgreSQL.
- **Utilities:** [`app/utils.py`](app/utils.py) — Helper functions for parsing.
- **Export:** [`app/save.py`](app/save.py) — GUI for exporting data to Excel.

---

## 📤 Exporting Data

To export all transactions to Excel:

```bash
python app/save.py
```
A simple GUI will appear. Click "Export to Excel Sheet" and the file will be saved in the path specified by `SAVEING_PATH`.

---

## 🐞 Troubleshooting

- **Airflow webserver not starting?**  
  Ensure ports 8080 and 5432 are free and Docker is running.

- **WhatsApp bot not downloading images?**  
  - Make sure Airflow is running and variables are set.
  - Scan the QR code on first run.
  - Check folder permissions.

- **OCR API errors?**  
  Check your endpoint and key in Azure Portal under your Vision Resource.

- **Database issues?**  
  Verify the path in your `.env` file and permissions.

---

## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

---

## 📄 License

This project is for educational and personal use. For commercial usage, please
