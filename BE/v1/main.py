from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json
from jaclang.runner import JacRunner  # ✅ this is the correct import for newer JacLang versions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="TaskVerse AI Backend")

# Load Jac file path
JAC_FILE_PATH = os.path.join(os.path.dirname(__file__), "main.jac")

# Initialize Jac runner (loads and executes Jac file once)
runner = JacRunner()
runner.run_file(JAC_FILE_PATH)

@app.get("/")
def home():
    return {"message": "Jac backend is live and ready!"}

@app.post("/walker/{walker_name}")
async def execute_walker(walker_name: str, request: Request):
    """Run a Jac walker dynamically (like taskverse_ai, get_all_tasks, etc.)"""
    try:
        payload = await request.json()
        result = runner.run_walker(walker_name, ctx=payload)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
