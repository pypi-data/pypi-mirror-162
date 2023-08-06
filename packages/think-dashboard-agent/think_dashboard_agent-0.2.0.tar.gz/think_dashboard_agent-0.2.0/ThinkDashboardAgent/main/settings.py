import enum
from ThinkDashboardAgent.providers.database_provider import DatabaseProvider
from ThinkDashboardAgent.providers.elasticsearch_provider import ElasticsearchProvider
from ThinkDashboardAgent.providers.redis_provider import RedisProvider
from ThinkDashboardAgent.providers.site_provider import SiteProvider
from ThinkDashboardAgent.providers.ssl_provider import SSLProvider


class SERVICE_TYPE(enum.Enum):
    ELASTICSEARCH: str = 'ELASTICSEARCH'
    DATABASE: str = 'DATABASES'
    SSL: str = 'SSL'
    SITE: str = 'SITE'
    REDIS: str = 'REDIS'


PROVIDERS = {
    'site': SiteProvider,
    'redis': RedisProvider,
    'ssl': SSLProvider,
    'databases': DatabaseProvider,
    'elasticsearch': ElasticsearchProvider
}
