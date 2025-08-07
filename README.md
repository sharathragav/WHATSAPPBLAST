# WhatsApp Bulk Sender

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A web application that automates sending bulk messages through WhatsApp Web using Selenium. Upload an Excel file of recipients, add media attachments, and watch messages go out in real time via a simple, intuitive interface.

---

## 🚀 Features

* **Bulk Messaging**: Send personalized messages to hundreds of contacts in one go.
* **Attachment Support**: Include images, videos, or documents with your messages.
* **Excel Integration**: Load recipient lists from `.xlsx` or `.xls` spreadsheets.
* **Real-Time Progress**: Monitor successes and failures as they happen.
* **Retry Logic**: Automatically retry failed sends with configurable limits.
* **Persistent Sessions**: Use your existing Chrome profile to stay logged into WhatsApp Web.
* **Drag & Drop**: Easy file uploads with in-browser validation.

---

## 🏗️ System Architecture

### Frontend

* **Framework**: React + TypeScript (built with Vite)
* **State Management**: TanStack React Query for caching and server-state sync
* **Routing**: Wouter for fast, lightweight client-side routes
* **Styling**: Tailwind CSS with custom WhatsApp-inspired theme
* **Components**: Modular UI based on shadcn/ui patterns
* **File Handling**: Drag-and-drop interface with instant validation feedback

### Backend

* **Framework**: Flask (Python)
* **Automation**: Selenium WebDriver controlling Chrome
* **Excel Parsing**: pandas + openpyxl/xlrd
* **Concurrency**: Background threads for non-blocking sends
* **Session**: Flask sessions secured by environment-based secret keys
* **CORS**: Enabled via Flask-CORS for frontend integration

---

## ⚙️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/whatsapp-bulk-sender.git
   cd whatsapp-bulk-sender
   ```

2. **Backend (Python)**

   * Create a virtual environment:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * Install dependencies:

     ```bash
     pip install -r requirements.txt
     ```
   * Environment variables (create a `.env` file):

     ```env
     FLASK_ENV=development
     SECRET_KEY=<your-secret-key>
     CHROME_PROFILE_PATH=/path/to/your/chrome/profile
     ```
   * Run the API server:

     ```bash
     flask run
     ```

3. **Frontend (Node.js)**

   * Install dependencies:

     ```bash
     npm install
     ```
   * Start development server:

     ```bash
     npm run dev
     ```
   * Open your browser at `http://localhost:5173`

---

## 📖 Usage

1. **Login**: The first time you load the app, it opens WhatsApp Web in Chrome. Scan the QR code if needed.
2. **Upload Recipients**: Drag-and-drop your Excel file (columns: `Name`, `Phone`, and optional `CustomMessage`).
3. **Compose Message**: Use templating tags like `{{Name}}` to personalize each message.
4. **Add Attachments (Optional)**: Drag-and-drop media files.
5. **Send**: Click `Start Sending` and watch the progress dashboard.
6. **Review Results**: Download a report of successes and failures.

---

## 🔧 Configuration

All settings live in `config.py` (backend) and `.env`:

| Variable              | Description                             | Default           |
| --------------------- | --------------------------------------- | ----------------- |
| `CHROME_PROFILE_PATH` | Path to your local Chrome user profile  | `~/.config/...`   |
| `MAX_RETRIES`         | Number of retry attempts for failures   | `3`               |
| `TIMEOUTS`            | Dict of operation timeouts (in seconds) | `{upload:30,...}` |

Adjust these to tune performance and reliability.

---

## 🛠️ Troubleshooting

* **Stuck on QR Code?** Ensure `CHROME_PROFILE_PATH` points to a profile already logged into WhatsApp Web.
* **Excel Errors?** Check that your file has valid phone numbers and no empty rows.
* **Slow Sends?** Increase `TIMEOUTS['send']` or reduce concurrency in `config.py`.
* **Chromedriver Issues?** Update to the latest ChromeDriver that matches your Chrome version.

---

## 📂 Project Structure

```bash
whatsapp-bulk-sender/
├── backend/
│   ├── app.py            # Flask server entrypoint
│   ├── sender.py         # Selenium automation logic
│   ├── config.py         # Timeout, retry, and path settings
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI parts
│   │   ├── hooks/        # Custom React hooks
│   │   └── App.tsx       # Main React component
│   ├── vite.config.ts    # Vite config
│   └── package.json      # Node dependencies
└── README.md
```

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built by Sharath Ragav T*
