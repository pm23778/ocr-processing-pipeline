# OCR Pipeline with FastAPI, Kafka, and Redis

This project is an **OCR Processing Pipeline** built using **FastAPI**, **Kafka**, and **Redis**.  
Users can upload an image, and the system processes it asynchronously using Kafka.  
You can track the **OCR processing status** in Redis in real time.

---

## 🚀 Features

### 🔹 Image Upload (FastAPI)
- Users upload an image through an API.
- API validates file type and size.

### 🔹 Kafka-based Asynchronous Processing
- Uploaded image is sent to a Kafka topic.
- Kafka consumer picks the message and performs OCR.
- This ensures fast, scalable, non-blocking processing.

### 🔹 OCR Extraction
- Extracts text from images using OCR engine.
- Works for JPG/PNG.

### 🔹 Redis Status Tracking
- When image is uploaded → Redis stores `"processing"`.
- After OCR complete → Redis stores `"completed"` with extracted text.
- Any client can fetch OCR status at any time.

---

## 🧠 How the Pipeline Works (In Simple Steps)

1. **User uploads image → FastAPI**
2. **FastAPI stores initial status in Redis ("processing")**
3. **FastAPI sends the image to Kafka Producer**
4. **Kafka Consumer reads message**
5. **Performs OCR processing**
6. **Updates Redis with OCR text + status ("completed")**
7. **Client fetches final OCR result from Redis**

---

## ▶️ Running the Project
docker-compose up --build

