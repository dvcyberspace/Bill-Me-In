from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json

# 1. APPLICATION CONFIGURATION
 
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. ENVIRONMENT VARIABLES & API CONFIGURATION
 
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 
# 3. EXTERNAL SERVICE INITIALIZATION
 
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

GEMINI_MODEL = "gemini-3.6-flash"

# 4. HOME PAGE
 
@app.route('/')
def home():
    """
    Serves the main Bill Me In frontend.
    """
    return send_from_directory('.', 'index.html')

# 5. BILL SEARCH & AI EXPLANATION

@app.route('/api/search', methods=['POST'])
def search_and_explain():
    """
    Searches for a Bill in Supabase and generates a
    source-grounded explanation using Gemini.

    Workflow:
        User Search
            ↓
        Supabase Bill Search
            ↓
        Retrieve Official Bill Text
            ↓
        Send Bill Text to Gemini
            ↓
        Generate Structured Explanation
            ↓
        Return Result to Frontend
    """

    # 5.1 Get and Validate Search Query
    data = request.get_json(silent=True) or {}

    search_query = data.get('query', '').strip()

    if not search_query:
        return jsonify({
            "error": "Search query is empty"
        }), 400


    # 5.2 Search Bills in Supabase
    try:
        response = (
            supabase
            .table("bills")
            .select("title, content, pdf_hash")
            .ilike(
                "title",
                f"%{search_query}%"
            )
            .limit(1)
            .execute()
        )

        bills = response.data

        if not bills:
            return jsonify({
                "error": "No matching bills found in the database."
            }), 404

        bill = bills[0]

        bill_title = bill.get("title")
        bill_content = bill.get("content")
        bill_hash = bill.get("pdf_hash")

        if not bill_content:
            return jsonify({
                "error": "The Bill was found, but its content is unavailable."
            }), 500

    except Exception as e:
        app.logger.error(f"Supabase error: {e}")

        return jsonify({
            "error": "Unable to retrieve the Bill from the database."
        }), 500


    # 5.3 Limit Document Size Sent to Gemini
    MAX_CHARS = 30000

    if len(bill_content) > MAX_CHARS:
        bill_text = (
            bill_content[:MAX_CHARS]
            + "\n\n[DOCUMENT TRUNCATED: "
              "Only the first 30,000 characters were provided to the AI.]"
        )
    else:
        bill_text = bill_content


    # 6. SOURCE-GROUNDED AI PROMPT
    prompt = f"""
You are a legal document summarizer for an application
called Bill Me In.

SOURCE:
The following text comes exclusively from an official Bill PDF
obtained from sansad.in.

STRICT RULES:

1. Base your answer ONLY on the provided document text.
2. Do NOT use outside knowledge.
3. Do NOT use news articles.
4. Do NOT use secondary sources.
5. Do NOT assume facts that are not present in the document.
6. Do NOT invent statistics.
7. Do NOT invent legal consequences.
8. Do NOT invent benefits or criticisms.
9. If the provided text does not contain enough information to answer a particular field, write:
   "I cannot verify this using the official sansad.in document."
10. Explain the Bill in simple English that an ordinary citizen can understand.
11. Keep the explanation factually grounded in the supplied official document text.
12. Do not tell the user whether the Bill is good or bad.
13. Do not provide political opinions or advice.
14. Explain concepts as if speaking to a 12-year-old.
15. Avoid unnecessary legal jargon.

Return ONLY a valid JSON object.
Do not use markdown.
Do not use code blocks.
Do not add introductory text.

The JSON must contain exactly these fields:

{{
    "what_is_it":
        "A simple 2-sentence explanation of what the Bill is about.",

    "who_affected":
        "Who is affected according to the document.",

    "what_stated":
        "The key provisions explicitly stated in the document.",

    "what_restricted":
        "Actions, rights, activities, or conduct that the document regulates or restricts."
}}

OFFICIAL BILL TEXT:

{bill_text}
"""

    # 7. GEMINI AI PROCESSING
    try:

        ai_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json"
            )
        )

        if not ai_response.text:
            raise ValueError("Gemini returned an empty response.")

        raw_text = ai_response.text.strip()


        # 7.1 Parse Gemini JSON Response
        try:
            explanation_data = json.loads(raw_text)

        except json.JSONDecodeError:

            # Handle accidental Markdown code fences
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]

            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]

            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            raw_text = raw_text.strip()

            explanation_data = json.loads(raw_text)


        # 8. RETURN BILL EXPLANATION
        return jsonify({
            "title": bill_title,
            "hash": bill_hash,
            "explanation": explanation_data
        })


    # 8.1 Handle Invalid AI Response
    except json.JSONDecodeError as e:

        app.logger.error(f"Gemini JSON error: {e}")

        return jsonify({
            "error": "Gemini returned an invalid explanation format.",
            "title": bill_title,
            "hash": bill_hash
        }), 502


    # 8.2 Handle Gemini/API Errors
    except Exception as e:

        app.logger.error(f"Gemini error: {e}")

        return jsonify({
            "error": "AI explanation is temporarily unavailable.",
            "title": bill_title,
            "hash": bill_hash
        }), 503

if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False
    )