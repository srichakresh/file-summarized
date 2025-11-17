import streamlit as st
import google.generativeai as genai
import os
import json
import pandas as pd
import tempfile
from dotenv import load_dotenv

# --- Load API key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠ Missing GOOGLE_API_KEY in your .env file.")
else:
    genai.configure(api_key=api_key)

# --- Initialize the Gemini model ---
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Streamlit page setup ---
st.set_page_config(page_title="Chat with Documents - Gemini", page_icon="📄", layout="centered")
st.title("📘 Chat with Documents using Gemini 2.0 Flash")

st.markdown("""
Upload a *PDF, **JSON, **TXT, or **CSV* file and ask Gemini to *summarize or answer questions* based on it.  
Built using *Google Generative AI SDK (v1.x)*.
""")

# --- File uploader (multi-format) ---
uploaded_file = st.file_uploader("📂 Upload a file", type=["pdf", "json", "txt", "csv"])

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def process_file(uploaded_file):
    """Read file content based on type and return (mime_type, content, text_version)."""
    ext = uploaded_file.name.split(".")[-1].lower()
    mime_type = None
    content = None
    text_data = ""

    if ext == "pdf":
        mime_type = "application/pdf"
        content = uploaded_file.read()
    elif ext == "json":
        data = json.load(uploaded_file)
        text_data = json.dumps(data, indent=2)
    elif ext == "txt":
        text_data = uploaded_file.read().decode("utf-8")
    elif ext == "csv":
        df = pd.read_csv(uploaded_file)
        text_data = df.head(10).to_string()  # sample of CSV content
    else:
        st.error("Unsupported file type.")
    
    return mime_type, content, text_data

if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    user_prompt = st.text_input(
        "💬 Ask something about this file",
        placeholder="e.g. Summarize this document, Find insights, Explain key points..."
    )

    if st.button("Ask Gemini") and user_prompt:
        mime_type, content, text_data = process_file(uploaded_file)

        with st.spinner("Generating response... ⏳"):
            try:
                if mime_type == "application/pdf":
                    # PDF input (binary)
                    response = model.generate_content(
                        [user_prompt, {"mime_type": mime_type, "data": content}]
                    )
                else:
                    # JSON, TXT, or CSV (text-based)
                    response = model.generate_content(f"{user_prompt}\n\n{text_data[:15000]}")

                answer = response.text
                st.session_state.chat_history.append(("🧑‍💻 You", user_prompt))
                st.session_state.chat_history.append(("🤖 Gemini", answer))
                st.success("✅ Response generated successfully!")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # --- Display chat history ---
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("🗨 Chat History")
        for sender, msg in st.session_state.chat_history:
            if sender == "🧑‍💻 You":
                st.markdown(f"{sender}:** {msg}")
            else:
                st.markdown(
                    f"<div style='background-color:#f1f1f1;padding:10px;border-radius:8px'>"
                    f"<b>{sender}:</b> {msg}</div>",
                    unsafe_allow_html=True
                )
else:
    st.info("📤 Please upload a PDF, JSON, TXT, or CSV file to begin.")