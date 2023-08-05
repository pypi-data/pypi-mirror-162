from imagination import container
from typing import Optional

from dnastack.client.factory import EndpointRepository
from dnastack.context.manager import ContextManager


class UnknownContextError(RuntimeError):
    pass


def use(registry_hostname_or_url: str, no_auth: Optional[bool] = False) -> EndpointRepository:
    """
    Initiate a client factory based on the given hostname, i.e., the name of the context.

    If the context does not exist, it will scan the given host server for the service
    registry API and use the API to import service endpoints from /services.

    The "in_isolation" argument is to prevent the current configuration from
    being created or modified. It is designed to use in the library. When it is
    set to "true", instead of loading the configuration from the configuration
    file, this method will use a dummy/blank configuration object.
    """
    manager: ContextManager = container.get(ContextManager)
    factory = manager.use(registry_hostname_or_url, no_auth=no_auth, in_isolation=True)
    if factory:
        return factory
    else:
        raise UnknownContextError(registry_hostname_or_url)