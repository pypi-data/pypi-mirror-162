from pathlib import Path
from typing import Union, List, Optional

import requests
import toml
from apscheduler.schedulers.blocking import BlockingScheduler
from pydantic import ValidationError

from think_dashboard_agent import types
from think_dashboard_agent.providers import DEFAULT_PROVIDERS


def __check_instances(instances: List, providers: Optional[dict] = None):
    _data = []

    if providers is None:
        providers = DEFAULT_PROVIDERS
    else:
        providers = {**DEFAULT_PROVIDERS, **providers}

    for instance in instances:
        provider = providers[instance.type]
        _instance_check_result = provider(instance).check()
        _data.append({
            'name': instance.name,
            'key': instance.key,
            'type': instance.type,
            'response': _instance_check_result.dict(),
        })
    return _data


def __run(session: requests.Session, config: types.Config, providers: Optional[dict] = None):
    _data = __check_instances(config.instance, providers)
    print(_data)
    # r = session.post(config.api_key, json=_data)
    # if r.status_code != 200:
    #     print(r.json())


def run(config_file: Union[str, Path], providers: Optional[dict] = None):
    """
    Run the agent.
    """
    with open(config_file) as f:
        _toml_file = toml.load(f)
    try:
        config = types.Config(**_toml_file)
        with requests.Session() as session:
            session.headers.update({'Authorization': f"Token {config.api_key}"})
            __run(session, config, providers)

    except ValidationError as e:
        print(e)


def run_forever(config_file: Union[str, Path], interval: int, providers: Optional[dict] = None):
    """
    Run the agent forever.
    """
    scheduler = BlockingScheduler()
    with open(config_file) as f:
        _toml_file = toml.load(f)
    try:
        config = types.Config(**_toml_file)
        with requests.Session() as session:
            session.headers.update({'Authorization': f"Token {config.api_key}"})
            scheduler.add_job(__run, 'interval', [session, config, providers], seconds=interval)
            scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
