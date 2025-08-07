## **WHATSAPP BLAST**

A professional web application for automating bulk messaging through WhatsApp Web with real-time progress tracking and a beautiful WhatsApp-themed interface.

---

## 🌟 Features

* **Professional Interface**: Clean, modern UI matching WhatsApp’s design language.
* **Manual Contact Entry**: Quick-add contacts with phone numbers and custom messages.
* **Excel Integration**: Upload `.xlsx`, `.xls`, or `.csv` files containing contact lists.
* **Real-time Tracking**: Live progress bar, statistics, and detailed logs.
* **Attachment Support**: Send images, documents, and files to all contacts.
* **Chrome Profile Integration**: Reuse existing Chrome profiles to maintain login sessions.
* **Retry Logic**: Configurable retries for failed message attempts.
* **Export & Templates**: Generate detailed reports and download Excel templates.
* **Drag & Drop Upload**: Intuitive file upload with visual feedback.

---

## 📋 Table of Contents

1. [Architecture]
2. [Prerequisites]
3. [Installation]
4. [Configuration]
5. [Usage]
6. [API Documentation]
7. [File Structure]
8. [Troubleshooting]
9. [Contributing]
10. [License]
11. [Acknowledgments]

---

## 🏗️ Architecture

**System Overview**

```
Frontend (HTML/CSS/JS) ←→ Flask API (Python) ←→ Selenium Automation
        ↓                   ↓                     ↓
   Static Files         File Storage          Chrome WebDriver
```

**Layer Breakdown**

* **Frontend**: Vanilla HTML5, CSS3, JS (ES6+); custom CSS in WhatsApp colors (`#075e54`, `#25d366`); drag-and-drop UI; responsive design.
* **Backend**: Flask 2.3+ (Python 3.8+); RESTful JSON endpoints; file handling via multipart forms; session management; CORS enabled.
* **Automation**: Selenium WebDriver; Chrome profile integration for session persistence; robust exception handling with retry logic.
* **Data Processing**: `pandas` for Excel parsing; supports `.xlsx`, `.xls`, `.csv`; automatic column detection; thread-safe progress tracking and logging.

---

## 🔧 Prerequisites

* **OS**: Linux, macOS, or Windows
* **Python**: 3.8+
* **Chrome**: Latest stable version
* **RAM**: ≥2 GB (4 GB+ recommended)
* **Disk**: ≥500 MB free

**Dependencies**

* Chrome WebDriver (managed by `webdriver-manager`)
* Python packages (see `requirements.txt`)
* Node.js (optional, for frontend development)

---

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/whatsapp-bulk-sender.git
   cd whatsapp-bulk-sender
   ```
2. **Set up a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   # Development mode
   python main.py

   # Production mode (with Gunicorn)
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

---

## ⚙️ Configuration

Customize `config.py` or set environment variables for:

| Variable               | Description                   | Default     | Required |
| ---------------------- | ----------------------------- | ----------- | :------: | 
| `CHROME_USER_DATA_DIR` | Chrome profile directory path | Auto-detect |    No    |
| `CHROME_PROFILE_NAME`  | Chrome profile name           | `Default`   |    No    |

Also adjust timeouts, retry settings, and file limits via the `CONFIG` dict in `config.py`.

---

## 🚀 Usage

1. **Open**: Navigate to `http://localhost:5000`.
2. **Add Contacts**:

   * **Quick Add**: Enter phone number (`+1234567890`), optional message, click *Add*.
   * **Excel Upload**: Drag & drop or browse. Ensure a `Contact` column; optional `Message` column.
3. **Start Sending**: Click *Start Sending*; scan QR code if prompted; monitor real-time progress.
4. **Attachments**: Upload files (`PDF`, `JPG`, `PNG`, `DOCX`, etc.). Text becomes the caption.

**Excel Format**

| Contact     | Message (Optional)               |
| ----------- | -------------------------------- |
| +1234567890 | Hello! This is a custom message. |
| +9876543210 | Hi there!                        |

Supported formats: `.xlsx`, `.xls`, `.csv`.

**Attachment Guidelines**

* **Formats**: PDF, JPG, PNG, GIF, DOC, DOCX, TXT
* **Max size**: 16 MB

---

## 📡 API Documentation

**Base URL**: `http://localhost:5000/api`

| Endpoint    | Method | Description              |
| ----------- | ------ | ------------------------ |
| `/send`     | POST   | Initiate bulk sending    |
| `/progress` | GET    | Retrieve live progress   |
| `/status`   | GET    | Check final status       |
| `/stop`     | POST   | Stop the ongoing process |
| `/health`   | GET    | Health check             |

**Example: Send**

```bash
curl -X POST http://localhost:5000/api/send \
  -F "recipientsFile=@contacts.xlsx" \
  -F "attachmentFile=@document.pdf"
```

**Example: Progress**

```json
GET /api/progress →
{
  "is_active": true,
  "current": 10,
  "total": 50,
  "success_count": 9,
  "failure_count": 1,
  "logs": [
    "[12:00:05] Sending to +1234567890...",
    "[12:00:10] ✅ Sent to +1234567890"
  ]
}
```

---

## 📁 File Structure

```
whatsapp-bulk-sender/
├── api/                # Flask route definitions
│   └── routes.py       # API endpoints
├── dist/public/        # Static frontend (HTML/CSS/JS)
│   └── index.html      # Main interface
├── shared/             # Shared utilities
├── uploads/            # Uploaded files storage
├── utils/              # Utility modules
│   └── file_handler.py # Excel parsing & validation
├── app.py              # Flask application factory
├── config.py           # Configuration settings
├── main.py             # Application entry point
├── sender.py           # Selenium automation core
├── requirements.txt    # Python dependencies
├── package.json        # Dev dependencies
└── README.md           # Project documentation
```

---

## 🔍 Troubleshooting

1. **ChromeDriver Issues**

   * *Not found* or version mismatch: ensure Chrome is up to date; reinstall `webdriver-manager`.
2. **QR Code Timeout**

   * Scan within 2 minutes; use a logged-in Chrome profile.
3. **Invalid Excel File**

   * Must contain `Contact` column; numbers in international format; valid file types.
4. **Permission Errors**

   * Ensure write access: `chmod 755 uploads/`.

*Enable debug logging*:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

*Process in batches* for large lists (50–100 contacts).

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/xyz`
3. Implement & test your changes
4. Ensure code style (PEP 8, ES6+, BEM for CSS)
5. Submit a Pull Request

**Testing**

```bash
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

* **WhatsApp Web** for the messaging UI
* **Selenium** for browser automation
* **Flask** for the web framework

---

<sup>⚠️ This tool is for educational and business compliance only. Ensure adherence to WhatsApp’s Terms of Service and relevant laws.</sup>
*Built by Sharath Ragav T*
