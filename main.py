from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles # <-- NEW
import google.generativeai as genai
import sqlite3
import os

app = FastAPI()

app.mount("/", StaticFiles(directory=".", html=True), name="static") # <-- NEW: this serves test.html

# Gemini setup
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Memory DB setup
conn = sqlite3.connect('aifo_memory.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS memory (password TEXT, history TEXT)''')
conn.commit()

def get_history(password):
    c.execute("SELECT history FROM memory WHERE password=?", (password,))
    row = c.fetchone()
    return row[0] if row else ""

def save_history(password, history):
    c.execute("REPLACE INTO memory (password, history) VALUES (?,?)", (password, history))
    conn.commit()

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    password = data.get("password")
    question = data.get("question")
    
    history = get_history(password)
    prompt = f"Previous chat: {history}\nUser: {question}\nAI:"
    
    response = model.generate_content(prompt)
    answer = response.text
    
    new_history = history + f"\nUser: {question}\nAI: {answer}"
    save_history(password, new_history)
    
    return JSONResponse({"answer": answer})

@app.get("/")
def read_root():
    return {"message": "Aifo Academy AI running with models/gemini-2.5-flash"}
