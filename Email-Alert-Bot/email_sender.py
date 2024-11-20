# email_sender.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from config import SMTP_SETTINGS

# Function to send an email
def send_email(recipient, subject, message_body):
    try:
        # Setting up SMTP session
        server = smtplib.SMTP(SMTP_SETTINGS['host'], SMTP_SETTINGS['port'])
        server.starttls()  # Secure the connection
        server.login(SMTP_SETTINGS['username'], SMTP_SETTINGS['password'])

        # Craft email
        msg = MIMEMultipart()
        msg['From'] = SMTP_SETTINGS['username']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        # Send email
        server.sendmail(SMTP_SETTINGS['username'], recipient, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function to retry sending email
def send_email_with_retry(recipients, subject, message_body, retries=3, delay=5):
    for recipient in recipients:
        for attempt in range(1, retries + 1):
            if send_email(recipient, subject, message_body):
                break
            elif attempt < retries:
                time.sleep(delay)
            else:
                print(f"Failed to send email to {recipient} after {retries} attempts.")
