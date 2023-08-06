import psycopg2

from think_dashboard_agent.types import DatabaseInstance
from .base import BaseProvider
from ..responses import InstanceCheckResult


class DatabaseProvider(BaseProvider):
    def __init__(self, instance: DatabaseInstance):
        self.instance = instance
        self.conn = None

    def exc(self):
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT count(table_name) 
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                    """)
        return cur.fetchone()[0]

    def check(self):
        try:
            self.connect()
            result = self.exc()
            return InstanceCheckResult(data=result)
        except psycopg2.OperationalError:
            return InstanceCheckResult(status=500, error='Unable to connect to the database')
        except psycopg2.Error as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            if self.conn:
                try:
                    self.conn.close()
                except psycopg2.Error:
                    pass

    # Create a connection to the database
    def connect(self):
        conn = psycopg2.connect(
            host=self.instance.host,
            port=self.instance.port,
            user=self.instance.username,
            password=self.instance.password,
            database=self.instance.database
        )
        self.conn = conn

    # Close the connection to the database
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
