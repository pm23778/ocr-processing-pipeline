import logging
from fastapi import APIRouter, File, HTTPException, UploadFile, Form,status
import uuid
import json
import os
from fastapi.responses import FileResponse
from app.services.kafka_producer import send_message
from app.services.redis_client import redis_client
from app.core.config import settings 
TOPIC = settings.kafka_topic 

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Setup logging
logger = logging.getLogger(__name__)



def save_file(file_id: str, file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read()) 
        return file_path
    except Exception as e:
        logger.error(f"File saving failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )

def send_to_kafka(message: dict):
    try:
        send_message(TOPIC, value=message)
    except Exception as e:
        logger.error(f"Kafka send failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send message to Kafka"
        )

def save_to_redis(file_id: str, message: dict):
    try:
        redis_client.set(file_id, json.dumps(message))
    except Exception as e:
        logger.error(f"Redis save failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to save file status in Redis"
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
         # Step 1: Generate unique ID and file path
        file_id = str(uuid.uuid4())
        file_path = save_file(file_id, file)
        message = {
            "file_id": file_id,
            "file_path": file_path,
            "filename": file.filename,
            "status": "uploading"
        }
        send_to_kafka(message)
        save_to_redis(file_id, message)
        
        return {"file_id": file_id, "status": "uploaded"}
        
        
    except HTTPException as http_exc: 
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error"
        )


BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

@router.get("/download/{filename}")
async def download_file(filename: str):
    # 1. uploads/ folder me check karo
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 2. agar uploads me nahi mila to root me check karo
    if not os.path.exists(file_path):
        file_path = os.path.join(BASE_DIR, filename)

    # 3. agar kahin bhi nahi mila to error
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 4. file return karo
    return FileResponse(file_path, media_type="image/png", filename=filename)