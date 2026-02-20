import json
import os
import smtplib
import time
from email.message import EmailMessage
from kafka import KafkaConsumer

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

TOPIC = "email_events"


def create_consumer():
    """Retry until Kafka is available."""
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_SERVER,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="email-service",
            )
            print("Connected to Kafka")
            return consumer
        except Exception as e:
            print("Kafka not ready, retrying in 5 seconds...")
            time.sleep(5)


def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    print("Email service starting...")
    consumer = create_consumer()

    print("Listening for email events...")

    for message in consumer:
        event = message.value

        event_type = event["event_type"]
        recipients = event["to"]

        subject = f"Notification: {event_type}"
        body = json.dumps(event.get("data", {}), indent=2)

        for email in recipients:
            send_email(email, subject, body)
            print(f"Email sent to {email} for event {event_type}")


if __name__ == "__main__":
    main()
