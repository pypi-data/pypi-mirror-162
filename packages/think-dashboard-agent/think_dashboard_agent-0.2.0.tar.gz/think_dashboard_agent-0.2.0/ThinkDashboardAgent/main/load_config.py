import json

import requests

from ThinkDashboardAgent.main.base import Config, get_data
from ThinkDashboardAgent.helpers.put_data import put_data
from ThinkDashboardAgent.main.settings import PROVIDERS


def config_list() -> list:
    l: list = []
    for i, j in get_data().items():
        l.append(Config(key=i))
    l.pop(0)
    l.pop(0)

    return l


def get_provider(config):
    try:
        return PROVIDERS.get(config.type)(config=config).check()
    except Exception as e:
        return e


def run():
    data: dict = {}
    for config in config_list():
        info = {
            'server': config.server,
            'status': get_provider(config),
            'type': config.type,
            'ip': config.ip,
            'port': config.port,
            'name': config.name,
            'key': config.key,
            'site_url': config.site_url,
        }
        data[config.key] = info
    put_data(data=data, token=get_data().get('token').get('token'))