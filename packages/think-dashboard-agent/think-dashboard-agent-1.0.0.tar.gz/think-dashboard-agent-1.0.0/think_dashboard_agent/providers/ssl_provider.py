import socket
import ssl
from datetime import datetime

from think_dashboard_agent.providers.base import BaseProvider
from think_dashboard_agent.responses import InstanceCheckResult
from think_dashboard_agent.types import SSLInstance


class SSLProvider(BaseProvider):
    def __init__(self, instance: SSLInstance):
        self.instance = instance
        self.conn = None

    def connect(self):
        if self.conn is None:
            context = ssl.create_default_context()
            self.conn = context.wrap_socket(
                socket.socket(socket.AF_INET),
                server_hostname=self.instance.host,
            )
            self.conn.settimeout(3.0)
            self.conn.connect((self.instance.host, self.instance.port))

    def exc(self):
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
        ssl_info = self.conn.getpeercert()
        expires = datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        return expires.strftime('%Y-%m-%d %H:%M:%S')

    def check(self) -> InstanceCheckResult:

        try:
            self.connect()
            return InstanceCheckResult(status=200, data=self.exc())
        except Exception as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
