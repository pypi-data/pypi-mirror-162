import redis
import os


class BaseRedisManager:
    client = None

    def __init__(self, store):
        self.redis_host = os.getenv('REDIS_HOST')
        self.redis_port = os.getenv('REDIS_PORT', '6379')
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.config_store = store

    def connect(self):
        self.client = redis.Redis(host=self.redis_host,
                                  port=int(self.redis_port),
                                  password=self.redis_password)
