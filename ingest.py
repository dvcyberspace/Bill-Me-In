import os
import hashlib
from pypdf import PdfReader
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Folder where official PDFs are stored
PDF_FOLDER = "bills_pdf"

def process_and_upload_pdfs():
    # Loop through all files in the bills_pdf folder
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            filepath = os.path.join(PDF_FOLDER, filename)
            print(f"Processing: {filename}...")

            # 1. Generate SHA-256 Fingerprint
            file_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
            sha256_fingerprint = file_hash.hexdigest()

            # 2. Extract Text using PyPDF
            extracted_text = ""
            try:
                reader = PdfReader(filepath)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except Exception as e:
                print(f"Error reading PDF {filename}: {e}")
                continue

            # 3. Clean up the title (just using the filename without .pdf for the MVP)
            bill_title = filename.replace(".pdf", "").replace("_", " ")

            # 4. Upload to Supabase 'bills' table
            try:
                data, count = supabase.table("bills").insert({
                    "title": bill_title,
                    "content": extracted_text,
                    "pdf_hash": sha256_fingerprint,
                    "status": "Verified on sansad.in"
                }).execute()
                print(f"✅ Successfully uploaded {bill_title} to Supabase!\n")
            except Exception as e:
                print(f"❌ Failed to upload {bill_title}: {e}")

if __name__ == "__main__":
    process_and_upload_pdfs()