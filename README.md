# 💸 Transaction Parser & OCR Pipeline

A robust, automated pipeline for extracting and organizing transaction data from financial receipts using OCR, with orchestration by Apache Airflow.

---

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/airflow-2.x-blue.svg)](https://airflow.apache.org/)

---

## 🖼️ Overview

This project watches a folder for new receipt images (e.g., WhatsApp downloads), extracts transaction data using OCR, classifies the transaction type, and stores the results in a local SQLite3 database. The entire process is modular and scheduled using Apache Airflow.

---

## 🚀 Features

- **Automated Folder Watching:** Detects new receipt images in a specified folder.
- **OCR Extraction:** Uses [OCR.Space API](https://ocr.space/) for accurate text extraction.
- **Transaction Classification:** Automatically distinguishes between Instapay and Vodafone Cash receipts.
- **Structured Data Storage:** Saves parsed data into a SQLite3 database.
- **Airflow Orchestration:** Modular, scheduled, and visualized pipeline management.
- **Duplicate Prevention:** Tracks processed images to avoid reprocessing.
- **Excel Export:** Easily export results for further analysis.

---

## ⚡ Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/payparser_pipeline.git
   cd payparser_pipeline
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your API keys and paths.

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Airflow with Docker:**
   ```bash
   cd airflow
   docker-compose up airflow-init
   docker-compose up
   ```

5. **Access Airflow UI:**
   - Visit [http://localhost:8080](http://localhost:8080) and trigger the `payparser_pipeline_dag`.

---

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
OCR_API_URL=...
OCR_API_KEY=...
DB_NAME=...
WATCH_FOLDER=...
SAVEING_PATH=...
AIRFLOW_PROJ_DIR=...
```

See `.env.example` for a template.

---

## 📁 Folder Structure

```
payparser_pipeline/
├── airflow/           # Airflow orchestration (DAGs, Docker config)
│   ├── dags/
│   │   └── payparser_dag.py
│   └── docker-compose.yaml
├── app/               # Core Python logic (OCR, parsing, DB)
│   ├── ocr.py
│   ├── parser.py
│   ├── db.py
│   ├── utils.py
│   └── ...
├── shared/            # Shared data (images, processed logs)
│   ├── downloads/
│   ├── processed_images.txt
│   └── tmp_result.json
├── requirements.txt
└── README.md
```

---

## 🛠️ Usage Example

- Place your receipt images in the `shared/downloads/` folder.
- The pipeline will automatically process new images, extract transaction data, and store it in the SQLite database.
- Export results to Excel using the provided tool in `app/save.py`.

---

## 🧱 Tech Stack

- **Python 3.12+**
- **Apache Airflow** (via Docker)
- **OCR.Space API**
- **SQLite3**
- **dotenv**
- *(Optional)* Node.js with Venom-Bot (for WhatsApp automation)

---

## 🐞 Troubleshooting

- **Airflow webserver not starting?**  
  Ensure ports 8080 and 5432 are free and Docker is running.
- **OCR API errors?**  
  Check your API key and usage limits at [OCR.Space](https://ocr.space/ocrapi).
- **Database issues?**  
  Verify the path in your `.env` file and permissions.

---

## 📄 License

This project is for educational and personal use. For commercial usage, please contact the maintainer.

---

## 🤝 Contributions

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes. Your input is valuable to enhance the project.
