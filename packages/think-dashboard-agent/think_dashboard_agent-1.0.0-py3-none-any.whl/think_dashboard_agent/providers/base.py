from think_dashboard_agent.responses import InstanceCheckResult


class BaseProvider:

    def connect(self):
        raise NotImplementedError()

    def exc(self, *args, **kwargs):
        raise NotImplementedError()

    def check(self) -> InstanceCheckResult:
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()
