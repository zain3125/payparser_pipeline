# Transaction Analysis and Management System
#### Description:

The **Transaction Analysis and Management System** is an advanced Python-based solution that utilizes **OCR (Optical Character Recognition)** to extract and analyze financial transaction details from images. The extracted data is then structured and stored in a **SQLite database**, making it easier to manage and analyze financial transactions. The system is designed to automate the process of extracting critical financial details such as transaction amount, sender, receiver’s phone number, and date, reducing manual efforts and potential errors.

## **Motivation for the Project:**
Managing financial transactions manually can be **time-consuming and error-prone**. Traditional methods involve manually recording details from receipts or bank statements, which can lead to mistakes and inefficiencies. This project aims to simplify and automate the process by using **OCR technology** combined with **Regular Expressions (Regex)** to accurately extract, store, and analyze transaction data.

## **How It Works:**
1. **Image Input:** The user provides the path to an image containing a financial transaction receipt.
2. **OCR Processing:** The image is sent to an **OCR API** for text recognition and extraction.
3. **Data Extraction:** Using **Regular Expressions (Regex)**, the system identifies and extracts key transaction details:
   - **Transaction Amount** (e.g., "250 EGP")
   - **Sender's Information** (e.g., email or account details)
   - **Receiver’s Phone Number** (e.g., "01012345678")
   - **Transaction Date and Time** (e.g., "15 February 2025 10:30 AM")
4. **Data Storage:** The extracted information is structured and stored in an **SQLite database**, organized by month and year for easy retrieval.
5. **Confirmation:** The system provides a confirmation message indicating that the transaction has been successfully stored in the database.

---

## **Project Files:**

### **1. `app.py` (Main Script):**
- Handles **image input** and **OCR API communication**.
- Extracts transaction details using **Regular Expressions (Regex)**.
- Saves transactions into an **SQLite database** (`transactions.db`).
- Validates extracted data before inserting it into the database.

### **2. `transactions.db` (Database):**
- Stores extracted transaction details.
- Organizes transactions in tables categorized by month and year.
- Used by `app.py` to insert and retrieve transaction data.

### **3. Image Files (`es.jpg`, `ok.jpg`, `photo.jpg`):**
- Sample transaction receipt images used for OCR testing and verification.

---

## **Key Features:**
- **Automated Data Extraction:** Extracts financial transaction details automatically from receipts.
- **High Accuracy:** Uses **OCR technology** combined with **Regex parsing** for reliable data extraction.
- **Database Integration:** Stores extracted data in **SQLite** for future analysis.
- **Month-wise Data Organization:** Creates separate tables for each month, allowing easier management.
- **Error Handling:** Implements multiple validation checks to handle potential errors and incorrect data formats.

---

## **Why These Technologies?**

### **1. Why Use an OCR API?**
Instead of implementing an in-house OCR engine, an **OCR API** was chosen for the following reasons:
- Higher accuracy in recognizing printed and handwritten text.
- Ease of integration with Python.
- Faster processing compared to open-source OCR solutions.

### **2. Why SQLite?**
- **Lightweight and Simple:** No need for an external database server.
- **Ideal for Local Storage:** Perfect for managing financial records without complex setups.
- **Structured Data Storage:** Tables are created dynamically to organize transactions month-wise.

### **3. Why Use Regular Expressions (Regex)?**
- **Efficient Data Extraction:** Enables precise pattern matching to extract amounts, dates, and phone numbers.
- **Flexible Parsing:** Works well with different receipt formats and structures.
- **Automates Text Processing:** Reduces the need for manual data entry and improves efficiency.

---

## **Technologies Used:**
- **Python** – Core logic, API communication, and data processing.
- **Requests** – For interacting with the OCR API.
- **SQLite3** – Lightweight database to store extracted transaction data.
- **Regular Expressions (Regex)** – For identifying and parsing key financial details from OCR text.
- **OCR API** – For extracting text from images efficiently.

---

## **Installation & Usage:**

### **1. Install Dependencies:**
```bash
pip install requests
```

### **2. Run the Application:**
```bash
python app.py
```

### **3. Provide User Inputs:**
- Enter the **receiver’s name** when prompted.
- Provide the **path to the transaction receipt image**.

### **4. Extracted Data Display:**
The system will output the extracted details, including:
- **Transaction Amount**
- **Sender’s Email/Details**
- **Receiver’s Phone Number**
- **Transaction Date & Time**
- **Table where the data was stored**

### **5. Access the Stored Data:**
The transactions are stored in an **SQLite database**. You can access and retrieve them using:
```bash
sqlite3 transactions.db
SELECT * FROM February_2025;
```

---

## **Error Handling & Debugging:**
- **Error 69:** OCR API response is invalid or missing.
- **Error 70:** JSON decoding failed due to incorrect response format.
- **Error 71:** Invalid table name (e.g., contains special characters).
- **Error 72:** Database insertion error.
- **Error 73:** Missing extracted transaction details.
- **Error 74:** OCR failed to extract any text from the image.

---

## **Future Improvements:**
- **Enhanced OCR Processing:** Use AI-powered OCR for even better accuracy.
- **Web Interface:** Develop a GUI for users to upload receipts directly.
- **Multi-language Support:** Extend text recognition for more languages.
- **Data Analytics Dashboard:** Implement a visualization system for transaction trends.

---

## **Conclusion:**
This **Transaction Analysis and Management System** automates the extraction and storage of financial transaction details from images. By using **OCR, Regex, and SQLite**, it offers a reliable and efficient way to manage financial records. The project can be further expanded to support additional features such as data analytics, cloud storage, and mobile application integration.

