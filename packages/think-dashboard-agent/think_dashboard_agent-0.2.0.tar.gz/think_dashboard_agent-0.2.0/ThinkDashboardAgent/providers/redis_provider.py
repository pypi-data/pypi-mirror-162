import redis
from ThinkDashboardAgent.main.base import BaseProveder


class RedisProvider(BaseProveder):

    def check(self) -> bool:

        r = redis.Redis(self.config.ip, self.config.port)
        try:
            r.ping()
            print("Successfully connected to redis")
            return True
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            print("Redis connection error!")
            return False
