from fastapi import FastAPI, Request
from pydantic import BaseModel
import os

# ---- Create FastAPI app ----
app = FastAPI()

# ---- Simple model for request ----
class UserInput(BaseModel):
    utterance: str
    session_id: str = ""

# ---- Health check route ----
@app.get("/")
def read_root():
    return {"message": "TaskVerse Backend is Live!"}

# ---- Mock AI response route ----
@app.post("/walker/taskverse_ai")
async def taskverse_ai(request: Request, data: UserInput):
    """Simulate AI Walker response (for frontend integration)"""
    message = data.utterance.strip()
    if not message:
        response_text = "Please type something!"
    else:
        response_text = f"AI Response: I received your message — '{message}'"

    # Simulate a consistent response structure
    return {
        "reports": [
            {
                "response": response_text,
                "session_id": data.session_id or "session_default_001"
            }
        ]
    }
