# notifier.py
from plyer import notification

def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Notification Bot",
        timeout=10  # Notification will stay for 10 seconds
    )
