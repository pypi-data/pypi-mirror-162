import json

import requests

from ThinkDashboardAgent.helpers.get_data import get_data


def put_data(data, token):
    url = get_data().get('url').get('DASHBOARD_URL')
    res = requests.post(
        url=url,
        headers={
            'Authorization': f'Token {token}',
        },
        json=json.dumps(data))
    return res.status_code
