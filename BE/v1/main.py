from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from email.mime.text import MIMEText
import smtplib
import os
from datetime import datetime

load_dotenv()
app = FastAPI()

# -------------------------------
# Utility
# -------------------------------
def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------
# Models
# -------------------------------
class Task(BaseModel):
    task: str
    date: str
    time: str
    deleted: bool = False

class Message(BaseModel):
    utterance: str
    date: str = ""
    time: str = ""
    new_task: str = ""
    email_subject: str = ""
    email_to: str = ""
    email_content: str = ""

# -------------------------------
# Session
# -------------------------------
class Session:
    def __init__(self):
        self.history = []
        self.created_at = get_current_datetime()

    def add_history(self, entry: str):
        self.history.append(entry)

    def get_history(self) -> str:
        return "\n".join(self.history[-10:])

session = Session()

# -------------------------------
# Task Handling
# -------------------------------
class TaskHandling:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: str, date: str, time: str) -> str:
        self.tasks.append(Task(task=task, date=date, time=time))
        return f"Task: {task}, Date: {date}, Time: {time} added successfully."

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
                return f"Task '{task_name}' updated to '{new_task}' on {new_date} at {new_time}."
        return f"Task '{task_name}' not found."

    def summarize_tasks(self) -> str:
        active_tasks = [t for t in self.tasks if not t.deleted]
        if not active_tasks:
            return "No active tasks."
        return "\n".join([f"- {t.task} on {t.date} at {t.time}" for t in active_tasks])

task_handler = TaskHandling()

# -------------------------------
# Email Handling
# -------------------------------
class EmailHandling:
    def send_email(self, email_content: str, email_subject: str, email_to: str) -> str:
        sender = os.getenv("SENDER_EMAIL")
        password = os.getenv("SENDER_PASSWORD")

        if not sender or not password:
            return "❌ Missing sender credentials."

        msg = MIMEText(email_content)
        msg["Subject"] = email_subject
        msg["From"] = sender
        msg["To"] = email_to

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email_to, msg.as_string())
            server.quit()
            return f"✅ Email sent to {email_to} with subject '{email_subject}'."
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"

email_handler = EmailHandling()

# -------------------------------
# General Chat
# -------------------------------
class GeneralChat:
    def chat(self, utterance: str) -> str:
        return f"You said: {utterance}"

chat_handler = GeneralChat()

# -------------------------------
# API Endpoints
# -------------------------------
@app.post("/task/add")
async def add_task(msg: Message):
    response = task_handler.add_task(msg.utterance, msg.date, msg.time)
    session.add_history(f"user: {msg.utterance}\nai: {response}")
    return {"response": response}

@app.post("/task/delete")
async def delete_task(msg: Message):
    response = task_handler.delete_task(msg.utterance)
    session.add_history(f"user: {msg.utterance}\nai: {response}")
    return {"response": response}

@app.post("/task/update")
async def update_task(msg: Message):
    response = task_handler.update_task(msg.utterance, msg.new_task, msg.date, msg.time)
    session.add_history(f"user: {msg.utterance}\nai: {response}")
    return {"response": response}

@app.get("/task/summarize")
async def summarize_tasks():
    response = task_handler.summarize_tasks()
    return {"response": response}

@app.post("/email/send")
async def send_email(msg: Message):
    response = email_handler.send_email(msg.email_content, msg.email_subject, msg.email_to)
    session.add_history(f"user: {msg.utterance}\nai: {response}")
    return {"response": response}

@app.post("/chat")
async def chat(msg: Message):
    response = chat_handler.chat(msg.utterance)
    session.add_history(f"user: {msg.utterance}\nai: {response}")
    return {"response": response}

