from fastapi import FastAPI
import google.generativeai as genai
import sqlite3
import os

app = FastAPI(title="Aifo Academy")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

conn = sqlite3.connect('aifo.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT, progress TEXT, history TEXT)''')
conn.commit()

SYSTEM_PROMPT = """
You are Aifo, the AI mentor for Aifo Academy.
Built by Morgan from Kisii.
You teach ethical hacking ONLY for legal education.
Be friendly, use Swahili + English + Sheng.
Give 1 concept + 1 lab + 1 question per message.
"""

@app.post("/register")
def register(username: str, password: str):
    try:
        c.execute("INSERT INTO users VALUES (?,?, 'Lesson 1', '')", (username, password))
        conn.commit()
        return {"reply": f"Karibu Aifo Academy {username}! Account imetengenezwa. Tuanze Lesson 1?"}
    except:
        return {"reply": "Username imechukuliwa already. Jaribu ingine."}

@app.post("/chat")
def chat(username: str, password: str, message: str):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if not user:
        return {"reply": "Wrong username or password. Use /register first"}

    history = user[3] + f"\nStudent: {message}"
    response = model.generate_content(SYSTEM_PROMPT + "\n" + history)

    new_history = history + f"\nAifo: {response.text}"
    c.execute("UPDATE users SET history=? WHERE username=?", (new_history, username))
    conn.commit()
    return {"reply": response.text}

@app.get("/")
def home():
    return {"message": "Aifo Academy AI is running. Built by Morgan from Kisii"}
