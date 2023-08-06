from typing import List, Literal, Dict

from pydantic import BaseModel, validator

from think_dashboard_agent.exceptions import ConfigParseException


class BaseInstance(BaseModel):
    key: str
    name: str = None
    type: Literal['database', 'redis', 'elasticsearch', 'ssl']
    host: str
    port: int


class DatabaseInstance(BaseInstance):
    username: str
    password: str
    database: str
    port: int = 5432


class RedisInstance(BaseInstance):
    password: str = None
    db: int = 1


class ElasticSearchInstance(BaseInstance):
    username: str
    password: str

    @validator('host')
    def validate_host(cls, v):
        if not v.startswith('http'):
            v = 'https://{}'.format(v)
        return v


class SSLInstance(BaseInstance):
    port: int = 443

    @validator('host')
    def validate_host(cls, v):
        if v.startswith('http://'):
            v = v.replace('http://', '')
        elif v.startswith('https://'):
            v = v.replace('https://', '')
        return v


INSTANCE_TYPES = {
    'database': DatabaseInstance,
    'redis': RedisInstance,
    'elasticsearch': ElasticSearchInstance,
    'ssl': SSLInstance,
}
ALLOWED_TYPES = list(INSTANCE_TYPES.keys())


class Config(BaseModel):
    api_key: str
    dashboard_url: str
    server_name: str
    instance: List[Dict]

    @validator('instance')
    def validate_instances(cls, v):
        _instances = []
        _keys = set()
        for instance in v:
            if 'type' not in instance:
                raise ConfigParseException('Instance must have a type')

            _instance_type = INSTANCE_TYPES[instance['type']]
            _instance = _instance_type(**instance)
            _instances.append(_instance)
            _keys.add(_instance.key)

        if len(_keys) != len(_instances):
            raise ConfigParseException('All instances must have a unique key')
        return _instances
