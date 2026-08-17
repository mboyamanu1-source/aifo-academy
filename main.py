import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai

app = FastAPI()

# Allow your website to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html
app.mount("/", StaticFiles(directory=".", html=True), name="static")


@app.get("/ask")
def ask(q: str):
    try:
        # Check if API key exists
        key = os.getenv("GEMINI_API_KEY")
        print("KEY EXISTS:", "YES" if key else "NO")  # This shows in Render logs
        
        if not key:
            return {"answer": "Error: GEMINI_API_KEY not found in Render Environment"}
        
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("You are Aifo Academy AI tutor from Kisii, Kenya. Answer clearly and helpfully: " + q)
        return {"answer": response.text}
    
    except Exception as e:
        print("ERROR:", e)
        return {"answer": f"Error: {str(e)}"}


# For Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
