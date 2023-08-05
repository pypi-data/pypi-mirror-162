from django.conf import settings

from .base_redis_manager import BaseRedisManager


class ConfigManager(BaseRedisManager):
    def __init__(self, service):
        super().__init__(
            f"{service}_{settings.REDIS_CONFIG_KEY}".upper()
        )
        if self.client is None:
            self.connect()

    def load(self):
        keys_ = self.client.hgetall(self.config_store)
        print("keys", keys_)
        values_ = self.client.hvals(self.config_store)
        all_keys = [x.decode('utf8') for x in keys_]
        all_values = [y.decode('utf8') for y in values_]
        config = dict()
        len_keys = len(all_keys)
        for index in range(len_keys):
            config.update({all_keys[index]: all_values[index]})

        print("Config loaded", config, sep='\n')
        return config

    def store(self, key, value):
        self.client.hset(self.config_store, key, value)

    def delete(self, key, value):
        self.client.hdel(self.config_store, key, value)
    
    def updateApiCall(self, daily_key):
        return self.client.hincrby(daily_key, "Request")
    
    def updateApiCallRequest(self, daily_key, msisdn):
        return self.client.lpush(daily_key, msisdn)

