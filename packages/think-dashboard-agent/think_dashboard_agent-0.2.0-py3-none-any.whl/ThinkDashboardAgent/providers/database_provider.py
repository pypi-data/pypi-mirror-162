import psycopg2
from ThinkDashboardAgent.main.base import BaseProveder


class DatabaseProvider(BaseProveder):
    def check(self) -> bool:

        status = ''
        try:
            conn = psycopg2.connect(
                host=self.config.ip,
                dbname=self.config.dbname,
                user=self.config.username,
                password=self.config.password,
                port=self.config.port
            )
            cur = conn.cursor()
            result = cur.execute(""" SELECT COUNT(tables) FROM information_schema.tables """)
            data = cur.fetchone()
            a = int(data[0])
            if a > 0:
                status = '200'
                print(status)
                return True
        except Exception as e:
            status = '500'
            print(status)
            return False
