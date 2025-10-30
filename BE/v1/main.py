from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple AI-like Responses ---
def ai_response(user_input: str) -> str:
    responses = {
        "hi": "Hey there! How can I help you today?",
        "hello": "Hello 👋! What task would you like me to manage?",
        "how are you": "I'm great, thanks for asking! Ready to help you with your tasks 😄",
        "who are you": "I’m TaskVerse AI — your smart task assistant!",
        "tell me a story": "Once upon a time, a developer deployed an app… and it finally worked flawlessly 😅",
    }
    # Default fallback response
    return responses.get(user_input.lower(), f"I heard you say '{user_input}'. Can you tell me more?")

# --- Root Endpoint ---
@app.get("/")
def root():
    return {"message": "✅ TaskVerse AI Backend is Live!"}

# --- Chat Endpoint ---
@app.post("/walker/taskverse_ai")
async def taskverse_ai(request: Request):
    data = await request.json()
    user_msg = data.get("utterance", "")
    response = ai_response(user_msg)
    return {
        "reports": [{
            "response": response,
            "session_id": "session_" + str(random.randint(1000, 9999))
        }]
    }

# --- Tasks Endpoint ---
@app.post("/walker/get_all_tasks")
async def get_all_tasks():
    return {
        "reports": [[
            {"id": "1", "context": {"task": "Complete deployment", "date": "2025-10-30", "time": "3:00 PM", "status": "Ongoing"}},
            {"id": "2", "context": {"task": "Test TaskVerse AI", "date": "2025-10-31", "time": "9:00 AM", "status": "Pending"}},
            {"id": "3", "context": {"task": "Finalize documentation", "date": "2025-11-01", "time": "10:30 AM", "status": "Done"}}
        ]]
    }

