from fastapi import FastAPI, Request
from jaclang import Jac
import json

app = FastAPI()

# Load your Jac file (make sure main.jac is in the same folder)
jac = Jac("main.jac")

@app.get("/")
def root():
    return {"message": "Backend is running and connected!"}

# Actual route for your AI walker
@app.post("/walker/taskverse_ai")
async def taskverse_ai(request: Request):
    data = await request.json()
    utterance = data.get("utterance", "")
    session_id = data.get("session_id", "")

    # Call your Jac walker (replace 'taskverse_ai' with your walker name inside main.jac)
    try:
        result = jac.run("taskverse_ai", ctx={"utterance": utterance, "session_id": session_id})
        return json.loads(result.json()) if hasattr(result, "json") else result
    except Exception as e:
        return {"error": str(e)}

# Optional route for fetching all tasks
@app.post("/walker/get_all_tasks")
async def get_all_tasks():
    try:
        result = jac.run("get_all_tasks")
        return json.loads(result.json()) if hasattr(result, "json") else result
    except Exception as e:
        return {"error": str(e)}
