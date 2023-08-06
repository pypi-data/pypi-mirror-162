import ssl
import socket
import datetime
from ThinkDashboardAgent.main.base import BaseProveder


class SSLProvider(BaseProveder):
    def check(self) -> bool:
        hostname = self.config.site_url
        # try:
        print(hostname)
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
        context = ssl.create_default_context()
        cann = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
        cann.connect((hostname, 443))
        ssl_info = cann.getpeercert()
        Exp_ON = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        Days_Remaining = Exp_ON - datetime.datetime.utcnow()
        print("Expires_ON: ", Exp_ON, "\nRemaining: ", Days_Remaining)
        print('-------------------------------------------------------------------------------')
        return True

    # except Exception as e:
    #     print(e)
    #     return False

    domains = ['google.com', 'youtube.com', 'yahoo.com', 'bx-finans.uz', 'letri.uz']

# res = SSLProvider(config=Config('server1_ssl')).check()
# print(res)
