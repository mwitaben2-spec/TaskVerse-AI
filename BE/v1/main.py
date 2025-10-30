from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import random
import datetime

app = FastAPI(title="TaskVerse AI Backend")

# ----------------------------
# BASIC IN-MEMORY SESSION DATA
# ----------------------------
sessions = {}

# ----------------------------
# SIMPLE AI SIMULATION
# ----------------------------
def simple_ai_response(user_input: str, session_id: str):
    """
    A lightweight AI-style function that simulates intelligent responses.
    It can tell stories, answer greetings, or discuss tasks.
    """
    user_input_lower = user_input.lower()

    # greetings
    if any(word in user_input_lower for word in ["hi", "hello", "hey", "how are you"]):
        responses = [
            "Hi there! I'm TaskVerse AI. How are you doing today?",
            "Hello 👋! I'm here to assist you with your tasks or chat!",
            "Hey! Hope you’re doing great. What can I do for you?"
        ]
        return random.choice(responses)

    # ask for story
    elif "story" in user_input_lower:
        stories = [
            "Once upon a time in Kuria land, two lovers defied tradition to be together. It’s a tale of courage, love, and redemption.",
            "Here’s a quick one: A farmer planted hope in dry land — and it blossomed into a forest. 🌳",
            "Once there was a coder who debugged through the night — and built the future before dawn!"
        ]
        return random.choice(stories)

    # task-related
    elif "task" in user_input_lower:
        return "Sure! Tell me your task details and I’ll help you schedule or remember them."

    # date or time questions
    elif "time" in user_input_lower:
        return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."

    elif "date" in user_input_lower:
        return f"Today's date is {datetime.date.today().strftime('%Y-%m-%d')}."

    # fallback generic
    else:
        replies = [
            "I received your message. Could you tell me more?",
            "Interesting... can you explain that a bit?",
            "Got it! What would you like me to do with that?",
        ]
        return random.choice(replies)

# ----------------------------
# API ROUTES
# ----------------------------

@app.get("/")
def home():
    return {"message": "✅ TaskVerse AI Backend is live!"}

@app.post("/walker/taskverse_ai")
async def chat_endpoint(request: Request):
    data = await request.json()
    utterance = data.get("utterance", "")
    session_id = data.get("session_id", "default")

    # Create new session if not exists
    if session_id not in sessions:
        sessions[session_id] = {"history": []}

    # Generate AI response
    response = simple_ai_response(utterance, session_id)
    sessions[session_id]["history"].append({"user": utterance, "ai": response})

    return JSONResponse({
        "reports": [
            {
                "session_id": session_id,
                "created_at": datetime.datetime.now().isoformat(),
                "response": response
            }
        ]
    })

@app.post("/walker/get_all_tasks")
async def get_tasks():
    # placeholder endpoint for the tasks tab in frontend
    fake_tasks = [
        {"task": "Finish Streamlit deployment", "date": "2025-10-30", "time": "15:00", "status": "Pending"},
        {"task": "Review project progress", "date": "2025-10-31", "time": "09:00", "status": "Scheduled"},
    ]
    return JSONResponse({"reports": [fake_tasks]})
