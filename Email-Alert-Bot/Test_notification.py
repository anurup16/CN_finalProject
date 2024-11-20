
from plyer import notification

def send_test_notification():
    notification.notify(
        title="Test Notification",
        message="This is a test message.",
        app_name="TestApp",
        timeout=10  # Duration in seconds
    )

if __name__ == "__main__":
    send_test_notification()
