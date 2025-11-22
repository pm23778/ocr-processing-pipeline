# FROM python:3.9

# WORKDIR /code

# COPY ./requirements.txt /code/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# # copy only app folder (clean builds)
# COPY ./app /code/app

# ENV PYTHONUNBUFFERED=1
# EXPOSE 8000

# # FastAPI start
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.9-slim

WORKDIR /code

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy only app folder (clean builds)
COPY ./app /code/app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# FastAPI start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
