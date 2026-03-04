import json
import os
from kafka import KafkaProducer
from prometheus_client import Counter

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

_producer = None

KAFKA_EVENTS = Counter("kafka_events_total", "Total Kafka Events Published", ["topic"])


def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda m: json.dumps(m).encode("utf-8"),
        )
    return _producer


def publish_event(topic: str, event: dict):
    producer = get_producer()
    producer.send(topic, event)
    KAFKA_EVENTS.labels(topic=topic).inc()
