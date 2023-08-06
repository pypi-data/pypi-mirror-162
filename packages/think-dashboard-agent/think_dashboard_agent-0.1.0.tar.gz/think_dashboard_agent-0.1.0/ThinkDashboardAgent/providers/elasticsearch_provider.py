import requests
from ThinkDashboardAgent.main.base import BaseProveder


class ElasticsearchProvider(BaseProveder):
    def check(self) -> bool:
        ip = self.config.data['ip']
        port = self.config.data['port']
        url = f'http://{ip}:{port}'
        try:
            res = requests.get(url=url)
            if res.status_code == 200 or res.status_code == 401:
                print(res.status_code)
                return True
        except Exception as e:
            print("Connection failed", e)
            return False
