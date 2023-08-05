from json import JSONDecodeError

import re
import requests
from imagination.decorator import service
from pydantic import BaseModel
from typing import Optional, List
from urllib.parse import urljoin, urlparse

from dnastack.cli.auth.manager import AuthManager
from dnastack.client.factory import EndpointRepository
from dnastack.client.models import ServiceEndpoint
from dnastack.client.service_registry.client import ServiceRegistry
from dnastack.client.service_registry.manager import ServiceRegistryManager
from dnastack.common.events import EventSource
from dnastack.common.logger import get_logger
from dnastack.configuration.manager import ConfigurationManager
from dnastack.configuration.models import Context, Configuration


class ContextMetadata(BaseModel):
    name: str
    selected: bool


@service.registered()
class ContextManager:
    _re_http_scheme = re.compile(r'^https?://')
    _logger = get_logger('ContextManager')

    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self.__events = EventSource(['context-sync', 'auth-begin', 'auth-disabled', 'auth-end'])

    @property
    def events(self):
        return self.__events

    def _get_hostname(self, hostname: str) -> str:
        base_url = hostname if self._re_http_scheme.search(hostname) else f'https://{hostname}'
        return urlparse(base_url).netloc

    def add(self, context_name: str):
        config = self._config_manager.load()

        assert context_name not in config.contexts, f'The context, called "{context_name}", already exists.'

        config.contexts[context_name] = Context()
        self._config_manager.save(config)

    def remove(self, context_name: str):
        config = self._config_manager.load()

        assert context_name in config.contexts, f'The context, called "{context_name}", does not exist.'

        del config.contexts[context_name]

        if config.current_context == context_name:
            config.current_context = None

        self._config_manager.save(config)

    def rename(self, old_name: str, new_name: str):
        config = self._config_manager.load()

        assert old_name in config.contexts, f'The context, called "{old_name}", does not exist.'
        assert new_name not in config.contexts, f'The context, called "{new_name}", already exists.'

        config.contexts[new_name] = config.contexts[old_name]
        del config.contexts[old_name]

        self._config_manager.save(config)

    def list(self) -> List[ContextMetadata]:
        config = self._config_manager.load()
        return [
            ContextMetadata(name=context_name,
                            selected=(config.current_context == context_name))
            for context_name in config.contexts.keys()
        ]

    def use(self,
            registry_hostname_or_url: str,
            context_name: Optional[str] = None,
            no_auth: Optional[bool] = False,
            in_isolation: bool = False) -> EndpointRepository:
        """
        Import a configuration from host's service registry (if available) or the corresponding public configuration
        from cloud storage. If "no_auth" is not set to True, it will automatically initiate all authentication.

        The "in_isolation" argument is to prevent the current configuration from being overridden. It is designed to
        use in the library mode. When it is set to "true", instead of loading the configuration from the configuration
        file, this method will use a dummy/blank configuration object.
        """
        target_hostname = self._get_hostname(registry_hostname_or_url)
        context_name = context_name or target_hostname

        context_logger = get_logger(f'{self._logger.name}/{context_name}')
        context_logger.debug(f'Begin the sync procedure (given: {registry_hostname_or_url}')

        config = self._config_manager.load() if not in_isolation else Configuration()
        context = config.contexts.get(context_name)
        is_new_context = context is None

        # Instantiate the service registry manager for the upcoming sync operation.
        reg_manager = ServiceRegistryManager(config, context_name, in_isolation)
        reg_manager.events.on('endpoint-sync', lambda e: self.events.dispatch('context-sync', e))

        # Trigger sync operation
        if is_new_context:
            context_logger.debug('Create a new context')
            reg_manager.in_isolation(True)

            exact_url_requested = self._re_http_scheme.search(registry_hostname_or_url)

            if exact_url_requested:
                registry = ServiceRegistry.make(ServiceEndpoint(id=context_name, url=registry_hostname_or_url))
            else:
                registry = self.registry(target_hostname)

            if registry:
                config.contexts[context_name] = Context()

                reg_manager.add_registry_and_import_endpoints(registry.endpoint.id,
                                                              registry.endpoint.url)
            else:
                raise RuntimeError(f'Failed to initiate a new context, called {context_name}, as the code cannot '
                                   'find the service registry endpoint')
        else:
            context_logger.debug('Update the existing context')
            active_registries = [e
                                 for e in config.contexts[context_name].endpoints
                                 if e.type in ServiceRegistry.get_supported_service_types()]
            reg_manager.in_isolation(len(active_registries) <= 1)
            for reg_endpoint in active_registries:
                reg_manager.synchronize_endpoints(reg_endpoint.id)

        # Set the current context.
        config.current_context = context_name

        # Save it to the configuration file.
        if not in_isolation:
            self._config_manager.save(config)

        # Initiate the authentication procedure.
        if no_auth:
            self.events.dispatch('auth-disabled', dict())
        else:
            auth_manager = AuthManager(config)

            # Set up an event relay.
            self.events.relay_from(auth_manager.events, 'auth-begin')
            self.events.relay_from(auth_manager.events, 'auth-end')

            auth_manager.initiate_authentications()

        # Then, return the repository.
        return EndpointRepository(config.contexts[context_name].endpoints, cacheable=True)

    @classmethod
    def registry(cls, hostname: str) -> Optional[ServiceRegistry]:
        # Scan the service for the list of service info.
        base_url = hostname if cls._re_http_scheme.search(hostname) else f'https://{hostname}'
        context_name = urlparse(base_url).netloc

        target_registry_url: Optional[str] = None

        # Base-registry-URL-to-listing-URL map
        potential_registry_base_paths = [
            # This is for a service which implements the service registry at root.
            '/',

            # This is for a collection service.
            '/service-registry/',

            # This is for an explorer service, e.g., viral.ai.
            '/api/service-registry/',
        ]

        for api_path in potential_registry_base_paths:
            registry_url = urljoin(base_url, api_path)
            listing_url = urljoin(registry_url, 'services')

            try:
                response = requests.get(listing_url, headers={'Accept': 'application/json'})
            except requests.exceptions.ConnectionError:
                continue

            if response.ok:
                try:
                    ids = sorted([entry['id'] for entry in response.json()])
                    cls._logger.debug(f'CHECK: IDS => {", ".join(ids)}')
                except JSONDecodeError:
                    # Look for the next one.
                    continue

                target_registry_url = registry_url

                break
            # end: if

        if target_registry_url:
            return ServiceRegistry.make(ServiceEndpoint(id=context_name, url=target_registry_url))
        else:
            return None
