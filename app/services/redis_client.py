import redis
import json
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)
print(redis_client,"redis_client")


def update_status(file_id: str, status: str, extra: dict = None):
    """Helper function to update Redis JSON for given file_id"""
    old_data = redis_client.get(file_id)
    if old_data:
        data = json.loads(old_data)
    else:
        data = {"file_id": file_id}

    data["status"] = status
    if extra:
        data.update(extra)

    redis_client.set(file_id, json.dumps(data))
    return data