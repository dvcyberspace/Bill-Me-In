# 📜 Bill Me In

> **Know the Bill. Know the Change. Stay Informed.**

Bill Me In is an AI-powered civic-tech platform that simplifies Indian government Bills and legislative documents into easy-to-understand explanations. 

The platform uses official government Bill documents as its source and leverages AI to explain complex legal content in simple language while maintaining neutrality and source traceability.

---

## ✨ Key Features

- **Source-Grounded AI** — Gemini explains Bills using *only* the official document content stored in our database.
- **Bill Search** — Instantly search and retrieve Bills dynamically.
- **Simple Explanations** — Understand what a Bill is, who it affects, what it states, and what it restricts, explained at a 12-year-old reading level.
- **Document Verification** — Cryptographic SHA-256 fingerprints identify the exact PDF used by the system to ensure zero tampering.
- **Automated PDF Ingestion** — Official Bills are automatically extracted, hashed, and stored for AI processing via a custom Python pipeline.

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3 (Tailwind CSS), Vanilla JavaScript
- **Backend:** Python + Flask
- **Database:** Supabase (PostgreSQL)
- **AI Integration:** Google Gemini API (`gemini-2.5-flash`)
- **PDF Processing:** PyPDF
- **Verification:** SHA-256 Cryptography
- **Data Source:** Digital Sansad (`sansad.in`)

---

## 🏗️ Architecture

```text
                 OFFICIAL BILL PDF (sansad.in)
                       │
                       ▼
                ┌─────────────┐
                │  ingest.py  │
                └─────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Extract Text       SHA-256 Hash
              │                 │
              └────────┬────────┘
                       ▼
                 ┌─────────┐
                 │ Supabase│
                 └─────────┘
                       │
                 (User Search)
                       ▼
                 ┌──────────┐
                 │  Flask   │
                 │ Backend  │
                 └──────────┘
                       │
                       ▼
                 ┌──────────┐
                 │ Gemini   │
                 │  API     │
                 └──────────┘
                       │
                       ▼
             Structured JSON Explanation
                       │
                       ▼
                  Bill Me In 
                   Frontend
```

## 📂 Project Structure

```text
Bill-Me-In/
│
├── app.py              # Flask backend & AI API routing
├── ingest.py           # PDF ingestion & database upload script
├── index.html          # Frontend UI
├── bills_pdf/          # Official Bill PDFs (Not committed to git)
├── requirements.txt    # Python dependencies
├── .env                # API credentials (Not committed to git)
└── README.md
```

## 🚀 Local Setup & Run

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/bill-me-in.git
cd bill-me-in
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Configure Supabase

Create a bills table with the following columns:

* `title` (text)
* `content` (text)
* `pdf_hash` (text)
* * `status` (text)

### 6. Add Bill PDFs

Place official Bill PDFs downloaded from Digital Sansad inside the `bills_pdf/` folder. (Note: This folder is excluded from version control).

### 7. Ingest the Bills

Run the data pipeline to extract text, generate hashes, and populate the database:

```bash
python ingest.py
```

### 8. Start the Flask server

```bash
python app.py
```

The application will run at `http://127.0.0.1:5000`. Open this URL in your browser to use Bill Me In!

## 🤖 AI Workflow

User searches for a Bill.

Flask queries Supabase and retrieves the official raw text.

Flask sends a strict, zero-hallucination prompt + raw text to Gemini.

Gemini generates a 5-point grounded explanation in JSON format.

The frontend unpacks the JSON and displays the explanation alongside the verified document hash.

**Note:** The AI is heavily prompt-engineered to refuse outside knowledge, prevent the invention of statistics, and maintain strict political neutrality.

## 🔮 Future Scope

**Continuous Tracking:** Automated scraping of Bills, Acts, and Gazette notifications from official sources.

**Bill Slides:** Transform lengthy Bills into concise visual slides

**Scan & Ask (Vision AI):** Upload physical newspaper clippings or legal documents for instant easy AI translation.

**Multilingual Support:** Voice interaction and native translations for Indian regional languages.

## ⚖️ Disclaimer

Bill Me In simplifies publicly available legislative information for educational and civic-awareness purposes. It does not provide legal advice. Explanations are AI-generated based exclusively on official source texts. The original government document remains the authoritative source.

> Bills affect everyone. Understanding them does too.
