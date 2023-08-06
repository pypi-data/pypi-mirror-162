import requests

from think_dashboard_agent.types import ElasticSearchInstance
from .base import BaseProvider
from ..responses import InstanceCheckResult


class ElasticSearchProvider(BaseProvider):
    def __init__(self, instance: ElasticSearchInstance):
        self.instance = instance
        self.conn = None

    def connect(self):
        self.conn = requests.Session()
        self.conn.auth = (self.instance.username, self.instance.password)
        self.conn.headers.update({'Content-Type': 'application/json'})

    def exc(self):
        return self.conn.get(f"{self.instance.host}:{self.instance.port}/_cluster/health")

    def check(self) -> InstanceCheckResult:
        try:
            self.connect()
            r = self.exc()
            if r.status_code == 200:
                return InstanceCheckResult(status=200, data=r.json())
            else:
                return InstanceCheckResult(status=r.status_code, error=r.text)
        except requests.exceptions.RequestException as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
