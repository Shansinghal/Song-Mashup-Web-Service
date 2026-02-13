import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

print(f"Testing email with User: {EMAIL_USER}")
# Do not print password for security, just length
print(f"Password length: {len(EMAIL_PASS) if EMAIL_PASS else 0}")

msg = EmailMessage()
msg['Subject'] = "Mashup Test Email"
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_USER # Send to self
msg.set_content("This is a test email from the Mashup generator debugger.")

try:
    print("Connecting to SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        print("Logging in...")
        smtp.login(EMAIL_USER, EMAIL_PASS)
        print("Sending message...")
        smtp.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"FAILED to send email details: {e}")
