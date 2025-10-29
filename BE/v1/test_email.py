import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
receiver_email = sender_email  # send to yourself for test

msg = MIMEText("The meeting that was scheduled for tomorrow has been postponed to a later day kindly bear with us. Sorry for the inconinience.")
msg["Subject"] = "Test Email"
msg["From"] = sender_email
msg["To"] = receiver_email

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.set_debuglevel(1)  # 👈 enable debug logs
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
