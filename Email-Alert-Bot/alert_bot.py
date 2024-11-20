import time
import logging
from datetime import datetime
import sqlite3
from email_sender import send_email_with_retry
from notifier import send_desktop_notification
from config import ALERT_RECIPIENTS, ALERT_COOLDOWNS, ALERT_HOURS

# Logging configuration
logging.basicConfig(filename='logs/alert_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Queue to store messages sent outside of alert hours
message_queue = []

# Flag to stop the process after sending a message
message_sent = False


# Database setup for notifications
def setup_database():
    conn = sqlite3.connect('data/notification_log.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications
                      (recipient TEXT, subject TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()


# Logging notifications to the database
def log_to_database(recipient, subject, message_body):
    conn = sqlite3.connect('data/notification_log.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifications VALUES (?, ?, ?, datetime('now'))",
                   (recipient, subject, message_body))
    conn.commit()
    conn.close()


# Determine if the current time is within the alert window
def is_within_alert_hours():
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute

    # Compare with start and end hours and minutes
    start_hour = ALERT_HOURS['start_hour']
    start_minute = ALERT_HOURS['start_minute']
    end_hour = ALERT_HOURS['end_hour']
    end_minute = ALERT_HOURS['end_minute']

    # Calculate the start and end times in minutes from midnight
    start_time_in_minutes = start_hour * 60 + start_minute
    end_time_in_minutes = end_hour * 60 + end_minute
    current_time_in_minutes = current_hour * 60 + current_minute

    # Check if the current time is within the alert time range
    return start_time_in_minutes <= current_time_in_minutes < end_time_in_minutes


# Check condition placeholder
def check_condition():
    return True


# Function to send queued messages after the alert window opens
def send_queued_messages():
    global message_sent  # Access the flag from the global scope

    if message_queue and not message_sent:  # Check if there are any messages in the queue and not yet sent
        for queued_message in message_queue:
            subject = queued_message['subject']
            message_body = queued_message['message_body']

            # Send email to all recipients
            send_email_with_retry(ALERT_RECIPIENTS, subject, message_body)

            # Send desktop notification
            send_desktop_notification("Queued Message Sent", message_body)

            # Log to file and database
            for recipient in ALERT_RECIPIENTS:
                logging.info(f"Queued notification sent to {recipient} with subject '{subject}'")
                log_to_database(recipient, subject, message_body)

        # Clear the queue after sending messages
        message_queue.clear()
        # Send a desktop notification that queued messages have been sent
        send_desktop_notification("Queued Messages Sent", "All queued messages have been sent successfully.")

        # Set the flag to stop the process after sending the queued message
        message_sent = True
    else:
        print("No queued messages to send.")


# Main function with cooldown and logging
def main():
    global message_sent  # Access the flag from the global scope

    setup_database()  # Set up the database at the start

    last_notification_time = 0
    alert_type = 'general'  # This can vary based on alert severity

    while not message_sent:  # Run an infinite loop until the message is sent
        if check_condition():
            current_time = time.time()
            cooldown_period = ALERT_COOLDOWNS.get(alert_type, ALERT_COOLDOWNS['general'])

            # Check cooldown before sending
            if current_time - last_notification_time > cooldown_period:
                subject = "Network Alert Notification"
                message_body = "This is a test alert notification from your network monitoring bot."

                # If within alert hours, send the notification
                if is_within_alert_hours():
                    send_email_with_retry(ALERT_RECIPIENTS, subject, message_body)
                    send_desktop_notification("Network Alert", message_body)
                    for recipient in ALERT_RECIPIENTS:
                        logging.info(f"Notification sent to {recipient} with subject '{subject}'")
                        log_to_database(recipient, subject, message_body)
                    last_notification_time = current_time
                    message_sent = True  # Set the flag to True after sending the first message
                else:
                    # If outside alert hours, queue the message
                    message_queue.append({'subject': subject, 'message_body': message_body})
                    print("Message queued for later delivery.")

            else:
                print("Cooldown active. No notification sent.")

            # Always check and send queued messages if inside alert window
            if is_within_alert_hours():
                send_queued_messages()  # Make sure to send the queued messages when the alert window is active

                # Stop the process after sending the queued message
                if message_sent:
                    print("Queued message sent. Stopping the process.")
                    break  # Exit the loop and stop the process

        else:
            print("Condition not met. No notification sent.")

        # Add a sleep time before checking again (to avoid busy-waiting)
        time.sleep(10)  # Check every 10 seconds (adjust as needed)

    print("Process finished.")


if __name__ == "__main__":
    main()
