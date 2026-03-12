import os
from celery import Celery
from upscale import get_upscaler

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

# In-memory storage for processed files (simulating a database/cache for bytes)
# In a real app, this should be a persistent storage like S3 or a DB,
# but since the task asks not to save to disk, we use Redis for the result or a global dict.
# Celery backend already stores the result.

@celery_app.task(bind=True)
def upscale_task(self, image_bytes):
    upscaler = get_upscaler()
    result_bytes = upscaler.upscale(image_bytes)
    return result_bytes
