# config.py
ALERT_RECIPIENTS = ["mohdasad2903@gmail.com"]  # Replace with actual recipient emails
ALERT_COOLDOWNS = {
    'general': 60  # Cooldown period in seconds for notifications
}

ALERT_HOURS = {
    'start_hour': 12,  # Start of alert hours (24-hour format)
    'start_minute': 56,  # Start minute
    'end_hour': 23,  # End of alert hours (24-hour format)
    'end_minute': 59,  # End minute
}

# SMTP configuration
SMTP_SETTINGS = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'wow9350@gmail.com',      # Replace with your email
    'password': 'oagtuxnbwsbiuvoz',             # Replace with your email password or app password
}
