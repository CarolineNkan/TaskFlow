import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body_html):
    host = os.getenv("MAIL_HOST")
    port = int(os.getenv("MAIL_PORT"))
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    from_email = os.getenv("MAIL_FROM")

    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(host, port) as server:
        server.login(username, password)
        server.sendmail(from_email, to_email, msg.as_string())

    print("Email sent successfully!")
