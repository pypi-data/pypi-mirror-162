import redis

from think_dashboard_agent.responses import InstanceCheckResult
from think_dashboard_agent.types import RedisInstance
from .base import BaseProvider


class RedisProvider(BaseProvider):
    def __init__(self, instance: RedisInstance):
        self.instance = instance
        self.conn = None

    def connect(self):
        conn = redis.Redis(
            host=self.instance.host,
            port=self.instance.port,
            password=self.instance.password,
            db=self.instance.db
        )
        self.conn = conn

    def exc(self):
        return self.conn.execute_command('PING')

    def check(self) -> InstanceCheckResult:
        try:
            self.connect()
            return InstanceCheckResult(data=self.exc())
        except redis.RedisError as e:
            return InstanceCheckResult(status=500, data={'error': str(e)})
        finally:
            self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None