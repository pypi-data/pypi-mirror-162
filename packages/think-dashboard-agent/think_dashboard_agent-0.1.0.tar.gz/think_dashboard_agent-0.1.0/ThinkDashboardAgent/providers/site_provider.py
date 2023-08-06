import requests
from ThinkDashboardAgent.main.base import BaseProveder


class SiteProvider(BaseProveder):
    def check(self) -> bool:
        url: str = self.config.site_url
        try:
            res = requests.get(url)
            if res.status_code == 200 or res.status_code == 401:
                print(res.status_code)
                return True
        except Exception as e:
            print(e)
            return False
