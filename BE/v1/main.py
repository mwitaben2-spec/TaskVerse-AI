from fastapi import FastAPI, Request
from jaclang import jac_interp
import os
import json

app = FastAPI()

# Path to your main.jac file
JAC_FILE_PATH = os.path.join(os.path.dirname(__file__), "main.jac")

# ✅ Preload Jac runtime
try:
    jac_runtime = jac_interp.JacInterp()
    jac_runtime.run(JAC_FILE_PATH)
    print("✅ Loaded Jac file successfully!")
except Exception as e:
    print(f"❌ Failed to load Jac file: {e}")


@app.get("/")
def root():
    return {"message": "Jac backend is live and connected!"}


@app.post("/walker/{walker_name}")
async def execute_walker(walker_name: str, request: Request):
    """
    Executes a walker (like taskverse_ai, get_all_tasks, etc.)
    defined in main.jac and returns its reports.
    """
    try:
        data = await request.json()
        utterance = data.get("utterance", "")
        session_id = data.get("session_id", "")

        # Run the walker
        result = jac_runtime.run(
            JAC_FILE_PATH,
            walker=walker_name,
            ctx={"utterance": utterance, "session_id": session_id},
        )

        return {"reports": result}
    except Exception as e:
        print("❌ Walker Execution Error:", e)
        return {"error": str(e)}
