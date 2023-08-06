from .database import DatabaseProvider
from .elasticsearch import ElasticSearchProvider
from .redis_provider import RedisProvider
from .ssl_provider import SSLProvider

DEFAULT_PROVIDERS = {
    'database': DatabaseProvider,
    'redis': RedisProvider,
    'elasticsearch': ElasticSearchProvider,
    'ssl': SSLProvider
}

__all__ = [
    'DatabaseProvider',
    'RedisProvider',
    'ElasticSearchProvider',
    'SSLProvider',
    'DEFAULT_PROVIDERS'
]
