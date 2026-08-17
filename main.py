from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import hashlib
import sqlite3

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# AUTO PICK THE FIRST WORKING MODEL
model_name = None
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        if 'gemini' in m.name:
            model_name = m.name
            break

if model_name is None:
    raise Exception("No Gemini model found")

model = genai.GenerativeModel(model_name)
print(f"USING MODEL: {model_name}") # this will show in Render logs

conn = sqlite3.connect('aifo_memory.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chats (user_id TEXT, role TEXT, message TEXT)''')
conn.commit()

class ChatRequest(BaseModel):
    password: str
    question: str

def get_user_id(password): return hashlib.sha256(password.encode()).hexdigest()
def get_history(user_id): 
    c.execute("SELECT role, message FROM chats WHERE user_id=? ORDER BY rowid", (user_id,))
    return c.fetchall()
def save_message(user_id, role, message): 
    c.execute("INSERT INTO chats VALUES (?,?,?)", (user_id, role, message))
    conn.commit()

@app.post("/ask")
async def ask_question(request: ChatRequest):
    if not request.password or not request.question: raise HTTPException(status_code=400, detail="Password and question required")
    user_id = get_user_id(request.password)
    history = get_history(user_id)
    chat = model.start_chat(history=[{'role': role, 'parts': [msg]} for role, msg in history])
    response = chat.send_message(request.question)
    answer = response.text
    save_message(user_id, 'user', request.question)
    save_message(user_id, 'model', answer)
    return {"answer": answer}

@app.get("/")
async def root(): return {"message": f"Aifo Academy AI running with {model_name}"}
