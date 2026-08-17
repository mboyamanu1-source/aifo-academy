import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This makes your index.html show when someone visits the site
app.mount("/", StaticFiles(directory=".", html=True), name="static")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/ask")
def ask(q: str):
    response = model.generate_content("You are Aifo Academy AI tutor from Kisii. Answer clearly: " + q)
    return {"answer": response.text}
