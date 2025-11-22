import os, json, time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from app.core.config import settings
BOOTSTRAP = settings.kafka_bootstrap_servers 


_producer = None

def _create_producer():
    last_err = None
    # Kafka up hone ke liye thoda wait + retry
    for attempt in range(30):  # ~60 seconds total (2s * 30)
        try:
            p = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=10,
                retries=5
            )
            return p
        except NoBrokersAvailable as e:
            last_err = e
            time.sleep(2)
    raise last_err

def send_message(topic: str, value):
    global _producer
    if _producer is None:
        _producer = _create_producer()
    fut = _producer.send(topic, value)
    _producer.flush(5)
    return fut
