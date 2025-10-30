from fastapi import FastAPI
import subprocess
import os

app = FastAPI()

@app.on_event("startup")
def compile_jac():
    try:
        subprocess.run(["jac", "build", "v1/main.jac"], check=True)
        print("✅ Jac file compiled successfully.")
    except Exception as e:
        print(f"⚠️ Jac compilation failed: {e}")

@app.get("/")
def home():
    return {"status": "Backend is live!", "message": "TaskVerse AI backend running fine."}
