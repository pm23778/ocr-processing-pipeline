import threading
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from app.api.router import upload
from app.services.kafka_consumer import  consume_messages
from app.services.kafka_producer import send_message
from app.core.config import settings 
import os

TOPIC = settings.kafka_topic 
app = FastAPI()

app.include_router(upload.router, prefix="/api")

@app.on_event("startup")
def start_kafka_consumer():
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()



