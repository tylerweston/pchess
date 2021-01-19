# # other celery setup goes here
# broker_url = 'redis://localhost:6379/0'
# result_backend = 'redis://localhost:6379/0'

broker_transport = "redis"

broker_host = "localhost"  # Maps to redis host.
broker_port = 6379         # Maps to redis port.
broker_vhost = "0"         # Maps to database number.

result_backend = "redis"
redis_host = "localhost"
redis_port = 6379
redis_db = 0