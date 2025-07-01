import streamlit as st
import requests
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="PDF Q&A Assistant", layout="wide")
st.title("📄 PDF Q&A Assistant")

# Upload PDF
uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

# Enter question
question = st.text_input("Ask your question about the PDF")

# Submit
if st.button("Get Answer") and uploaded_file and question.strip():
    with st.spinner("Sending request to FastAPI..."):
        try:
            files = {
                "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
            }
            data = {
                "question": question
            }
            response = requests.post("https://ask-your-pdf-zoqy.onrender.com", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Answer:")
                st.write(result["answer"])
            else:
                st.error(f"❌ FastAPI error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to FastAPI: {e}")
else:
    st.info("📌 Upload a PDF and ask a question to get started.")


# ✅ Show Previous Q&A
st.subheader("🕘 Q&A History")

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    df = pd.read_sql("SELECT question, answer, timestamp FROM qa_logs ORDER BY timestamp DESC LIMIT 10", conn)
    st.dataframe(df)
    conn.close()
except Exception as e:
    st.error(f"Failed to fetch history: {e}")