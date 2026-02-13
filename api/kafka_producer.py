import json
import os
from kafka import KafkaProducer

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = "email_events"

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
        )
    return _producer


def send_email_event(event: dict):
    producer = get_producer()
    producer.send(TOPIC, event)
    producer.flush()
