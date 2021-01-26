# Celery and redis configuration
#
# broker_transport = "redis"
#
# broker_host = "redis"  # Maps to redis host.
# broker_port = 6379         # Maps to redis port.
# broker_vhost = "0"         # Maps to database number.
broker_url = 'redis://redis:6379'

result_backend = 'redis://redis:6379'