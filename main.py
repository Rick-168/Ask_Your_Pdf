from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from db import QALog, SessionLocal  # ✅ DB model
from typing import Optional
from llm_logic import get_ans 
app = FastAPI()

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_pdf(question: str = Form(...), file: UploadFile = File(...)):
    # Placeholder logic
    content = await file.read()
    file_size_kb = len(content) / 1024

    # Calling LLM
    answer = get_ans(content, question)

    # ✅ Save to PostgreSQL
    db = SessionLocal()
    qa_record = QALog(question=question, answer=answer)
    db.add(qa_record)
    db.commit()
    db.close()

    return {
        "answer": f"{answer}",
        "file_info": f"Received file '{file.filename}' ({file_size_kb:.2f} KB)"
    }
