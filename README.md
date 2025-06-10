# Transaction Parser & OCR System

This project is a WhatsApp-based transaction parsing system that extracts, processes, and stores financial receipts (e.g., Instapay & Vodafone Cash) using OCR.

## 📌 Features

- ✅ Automatically listens to WhatsApp group messages.
- 🖼 Extracts and saves image receipts to categorized folders.
- 🔍 Uses [OCR.Space API](https://ocr.space/) to extract text from images.
- 🗃 Stores parsed data in a local SQLite3 database.
- 🧠 Built with Python for data parsing and Node.js (Venom Bot) for WhatsApp automation.

---

## 🧱 Tech Stack

- 🐍 **Python** (Data parsing, OCR, SQLite3)
- 💬 **Node.js** with [Venom-Bot](https://github.com/orkestral/venom) (WhatsApp automation)
- 🗄 **SQLite3** (Local storage)
- 🔐 **dotenv** for managing private configs

---

## 🗂 Project Structure

```
payparser_pipeline/
│
├── app/
│   ├── config.py        # Load environment variables
│   ├── db.py            # Database connection
│   ├── main.py          # Entry point for parser
│   ├── ocr.py           # OCR processing logic
│   ├── parser.py        # Text analysis & parsing
│   ├── save.py          # Save logic to DB/Excel
│   ├── utils.py         # Helper functions
│   └── watcher.py       # Watch folder for new images
│
├── whatsapp-bot/
│   └── index.js         # WhatsApp automation using venom-bot
│
├── .env                 # Environment variables
├── .gitignore           # Files to ignore
└── README.md            # You are here!
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/zain3125/Transaction-Management-System.git
cd Transaction-Management-System
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies

```bash
cd whatsapp-bot
npm install
```

### 4. Configure Environment Variables

Create a `.env` file in the root folder:

```env
OCR_API_URL=https://api.ocr.space/parse/image
OCR_API_KEY=your_ocr_api_key

DB_NAME=./data_bases/system_data.db
WATCH_FOLDER=./whatsapp-bot/downloads
SAVEING_PATH=./Excell_sheets
```

### 5. Start the Application

```bash
# Run the WhatsApp bot (Node.js)
node whatsapp-bot/index.js

# Run the watcher/parser (Python)
python app/main.py
```

---

## 🚫 .gitignore (Already included)

- Database files (`*.db`)
- Excel/CSV files
- Node modules (`node_modules/`)
- Token & cache folders
- JSON files

---

## 📄 License

This project is for educational and personal use. If you plan to use it commercially, please contact the owner.

---

## 🤝 Contributions

Pull requests are welcome! Feel free to fork and suggest improvements.
