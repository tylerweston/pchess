# Celery and redis configuration
import os
broker_url = os.getenv("REDIS_URL")
result_backend = os.getenv("REDIS_URL")