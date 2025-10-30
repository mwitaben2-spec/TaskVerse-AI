# main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from email.mime.text import MIMEText
import smtplib
import os
from byllm.llm import Model
from utils import get_current_datetime

load_dotenv()
app = FastAPI()
llm = Model(model_name="gemini/gemini-2.5-flash", verbose=False)

# -------------------------------
# Models
# -------------------------------

class Task(BaseModel):
    task: str
    date: str
    time: str
    deleted: bool = False

class Session(BaseModel):
    history: list[str] = []
    created_at: str = get_current_datetime()

    def add_history(self, entry: str):
        self.history.append(entry)

    def get_history(self) -> str:
        return "\n".join(self.history[-10:])

# -------------------------------
# Task Handling
# -------------------------------

class TaskHandling:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: str, date: str, time: str) -> str:
        self.tasks.append(Task(task=task, date=date, time=time))
        return "Task added successfully."

    def delete_task(self, task_name: str) -> str:
        for t in self.tasks:
            if not t.deleted and t.task == task_name:
                t.deleted = True
                return f"Task '{task_name}' deleted successfully."
        return f"Task '{task_name}' not found."

    def update_task(self, task_name: str, new_task: str, new_date: str, new_time: str) -> str:
        for t in self.tasks:
            if not t.deleted and t.task == task_name:
                t.task = new_task
                t.date = new_date
                t.time = new_time
                return f"Task '{task_name}' updated successfully to '{new_task}' scheduled for {new_date} at {new_time}."
        return f"Task '{task_name}' not found."

    def check_scheduled_tasks(self) -> list[Task]:
        return [t for t in self.tasks if not t.deleted]

    def extract_task_info(self, utterance: str) -> str:
        return llm.run("ReAct", tools=[self.add_task, get_current_datetime], input=utterance)

    def summarize_tasks(self) -> str:
        return llm.run("ReAct", tools=[self.check_scheduled_tasks])

    def route_and_run(self, utterance: str, history: str) -> str:
        return llm.run("ReAct", tools=[
            self.extract_task_info,
            self.summarize_tasks,
            self.delete_task,
            self.update_task
        ], input={"utterance": utterance, "history": history})

# -------------------------------
# Email Handling
# -------------------------------

class EmailHandling:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

    def send_email(self, email_content: str, email_subject: str, email_to: str) -> str:
        if not self.sender_email or not self.sender_password:
            return "❌ Missing sender credentials."

        msg = MIMEText(email_content)
        msg["Subject"] = email_subject
        msg["From"] = self.sender_email
        msg["To"] = email_to

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, email_to, msg.as_string())
            server.quit()
            return f"✅ Email sent successfully to {email_to} with subject '{email_subject}'."
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"

    def route_and_run(self, utterance: str, history: str) -> str:
        return llm.run("ReAct", tools=[self.send_email], input={"utterance": utterance, "history": history})

# -------------------------------
# General Chat
# -------------------------------

class GeneralChat:
    def chat(self, utterance: str, history: str) -> str:
        return llm.run("ReAct", tools=[], input={"utterance": utterance, "history": history})

# -------------------------------
# API Endpoints
# -------------------------------

session = Session()
task_handler = TaskHandling()
email_handler = EmailHandling()
chat_handler = GeneralChat()

@app.post("/task")
async def handle_task(request: Request):
    data = await request.json()
    utterance = data.get("utterance", "")
    response = task_handler.route_and_run(utterance, session.get_history())
    session.add_history(f"user: {utterance}\nai: {response}")
    return {
        "session_id": id(session),
        "created_at": session.created_at,
        "response": response
    }

@app.post("/email")
async def handle_email(request: Request):
    data = await request.json()
    utterance = data.get("utterance", "")
    response = email_handler.route_and_run(utterance, session.get_history())
    session.add_history(f"user: {utterance}\nai: {response}")
    return {
        "session_id": id(session),
        "created_at": session.created_at,
        "response": response
    }

@app.post("/chat")
async def general_chat(request: Request):
    data = await request.json()
    utterance = data.get("utterance", "")
    response = chat_handler.chat(utterance, session.get_history())
    session.add_history(f"user: {utterance}\nai: {response}")
    return {
        "session_id": id(session),
        "created_at": session.created_at,
        "response": response
    }

