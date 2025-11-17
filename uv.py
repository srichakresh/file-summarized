import pathlib
import os
import json
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# --- Load API key ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Model ---
model = genai.GenerativeModel("gemini-2.0-flash")

# --- File paths (update these as per your folder) ---
pdf_path = pathlib.Path("data/what is semisupervised ml.pdf")
json_path = pathlib.Path("data\sample.json")
txt_path = pathlib.Path("data\OOPs_practicals.txt")
csv_path = pathlib.Path("data\weatherPrediction.csv")

# --- Function to summarize based on file type ---
def summarize_file(filepath):
    ext = filepath.suffix.lower()
    prompt = "Summarize this document in simple terms."

    # --- For PDF ---
    if ext == ".pdf":
        with open(filepath, "rb") as f:
            response = model.generate_content(
                [prompt, {"mime_type": "application/pdf", "data": f.read()}]
            )
        return response.text

    # --- For JSON ---
    elif ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        text = json.dumps(data, indent=2)
        response = model.generate_content(f"{prompt}\n\n{text[:15000]}")
        return response.text

    # --- For Text ---
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        response = model.generate_content(f"{prompt}\n\n{text[:15000]}")
        return response.text

    # --- For CSV ---
    elif ext == ".csv":
        df = pd.read_csv(filepath)
        sample = df.head(10).to_string()  # summarize first 10 rows
        response = model.generate_content(f"{prompt}\n\nHere is the data:\n{sample}")
        return response.text

    else:
        return "Unsupported file type. Please provide PDF, JSON, TXT, or CSV."

# --- Run summarizer for all files ---
for file in [pdf_path, json_path, txt_path, csv_path]:
    if file.exists():
        print(f"\n--- Summary for {file.name} ---\n")
        print(summarize_file(file))
    else:
        print(f"\n⚠ File not found: {file}\n")