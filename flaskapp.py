from flask import Flask, request, jsonify
import tempfile
import os
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# --- Load .env variables ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in environment variables or .env")

# --- Configure Gemini ---
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Flask app setup ---
app = Flask(__name__)

# ---------------------------------------------------------
# NEW ROUTE: /analyze → handles PDF, JSON, TXT, and CSV
# ---------------------------------------------------------
@app.route("/analyze", methods=["POST"])
def analyze_file():
    """
    POST /analyze
    Form-data:
      - file: File (pdf/json/txt/csv)
      - prompt: text prompt or question
    """
    try:
        # --- Validate inputs ---
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": "Please provide a text prompt"}), 400

        uploaded_file = request.files["file"]
        filename = uploaded_file.filename.lower()

        # --- Determine file type ---
        if filename.endswith(".pdf"):
            mime_type = "application/pdf"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                uploaded_file.save(tmp_file.name)
                pdf_path = tmp_file.name

            with open(pdf_path, "rb") as f:
                file_bytes = f.read()

            response = model.generate_content(
                [prompt, {"mime_type": mime_type, "data": file_bytes}]
            )

            os.remove(pdf_path)

        elif filename.endswith(".json"):
            data = json.load(uploaded_file)
            text_data = json.dumps(data, indent=2)
            response = model.generate_content(f"{prompt}\n\n{text_data[:15000]}")

        elif filename.endswith(".txt"):
            text_data = uploaded_file.read().decode("utf-8")
            response = model.generate_content(f"{prompt}\n\n{text_data[:15000]}")

        elif filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            sample = df.head(10).to_string()
            response = model.generate_content(f"{prompt}\n\nHere is the data:\n{sample}")

        else:
            return jsonify({"error": "Unsupported file type. Please upload PDF, JSON, TXT, or CSV."}), 400

        return jsonify({
            "filename": uploaded_file.filename,
            "prompt": prompt,
            "answer": response.text.strip() if response.text else "(No text response returned)"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# (Optional) keep your original /process route
@app.route("/process", methods=["GET"])
def process_info():
    return jsonify({
        "message": "Use POST /analyze to upload and analyze PDF, JSON, TXT, or CSV files."
    })


if __name__ == "__main__":
    app.run(debug=True)