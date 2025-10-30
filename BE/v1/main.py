from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json
from jaclang import JacProgram  # ✅ Works with JacLang >=0.8.10
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="TaskVerse AI Backend")

# Path to your Jac file
JAC_FILE_PATH = os.path.join(os.path.dirname(__file__), "main.jac")

# ✅ Load and compile your Jac code once at startup
jac_program = JacProgram.load(JAC_FILE_PATH)

@app.get("/")
def home():
    return {"message": "Jac backend is live and working!"}

@app.post("/walker/{walker_name}")
async def run_walker(walker_name: str, request: Request):
    """Run a Jac walker such as 'taskverse_ai' or 'get_all_tasks'"""
    try:
        data = await request.json()
        # Execute walker on the Jac program
        result = jac_program.run_walker(walker_name, ctx=data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
