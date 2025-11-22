print("=========================>")
import os
import json
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from app.services.ocr import OCRPreprocessor
from app.services.redis_client import redis_client, update_status
from app.core.config import settings



BOOTSTRAP = settings.kafka_bootstrap_servers
TOPIC = settings.kafka_topic
GROUP_ID = settings.kafka_group_id

_consumer = None


def _create_consumer():
    last_err = None
    # Kafka up hone ka wait + retry
    for attempt in range(30):  # 60 seconds total (2s * 30)
        try:
            c = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",  # earliest → पुराने messages भी consume
                enable_auto_commit=True,       # auto commit offset
                # consumer_timeout_ms=1000      # 1 second wait, फिर StopIteration
            )
            return c
        except NoBrokersAvailable as e:
            last_err = e
            time.sleep(2)
    raise last_err


def get_consumer():
    """
    Global consumer object return kare.
    Agar pehli baar hai to create kare, warna reuse kare.
    """
    global _consumer
    if _consumer is None:
        _consumer = _create_consumer()
    return _consumer

def consume_messages():
    consumer = get_consumer()
    for message in consumer:
        data = message.value
        
        file_id = data["file_id"]
        file_path = data["file_path"]
        filename = data.get("filename", "unknown")
        
        update_status(file_id, "processing")
        try:
            policies = {
            "quality_check": {"enabled": True, "threshold": 5.0},
            "grayscale": True,
            "denoise": True,
            "contrast_enhance": True,
            "resize": {"dpi": 300}
            }
            preprocessor = OCRPreprocessor(image_path=file_path, policies=policies)
            processed_path = preprocessor.run_pipeline()
            # OCR complete hone ke baad Redis update
            update_status(file_id, "processed", {"processed_path": processed_path})
            print(f"OCR Preprocessing Done → {processed_path}")
        except Exception as e:
            # Agar error aaya to status failed
            update_status(file_id, "failed")
            print(f"Failed file: {filename} (ID: {file_id}), Error: {e}")
            
 
        
        