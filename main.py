import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai

app = FastAPI()

# Allow your website to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API ROUTE FIRST - This must come before static files
@app.get("/ask")
def ask(q: str):
    try:
        key = os.getenv("GEMINI_API_KEY")
        print("KEY EXISTS:", "YES" if key else "NO")
        
        if not key:
            return {"answer": "Error: GEMINI_API_KEY not found in Render Environment"}
        
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content("You are Aifo Academy AI tutor from Kisii, Kenya. Answer clearly: " + q)
        return {"answer": response.text}
    
    except Exception as e:
        print("ERROR:", e)
        return {"answer": f"Error: {str(e)}"}


# 2. STATIC FILES LAST - serve index.html
app.mount("/", StaticFiles(directory=".", html=True), name="static")


# For Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
