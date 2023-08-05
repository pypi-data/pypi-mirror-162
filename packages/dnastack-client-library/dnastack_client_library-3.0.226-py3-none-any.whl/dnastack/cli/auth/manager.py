from pydantic import Field
from typing import Optional, List, Any, Dict, Iterator, Callable

from dnastack.client.models import ServiceEndpoint
from dnastack.common.events import EventSource
from dnastack.common.logger import get_logger
from dnastack.common.model_mixin import JsonModelMixin
from dnastack.configuration.models import Configuration
from dnastack.configuration.wrapper import ConfigurationWrapper
from dnastack.http.authenticators.abstract import Authenticator, AuthStateStatus, AuthState
from dnastack.http.authenticators.factory import HttpAuthenticatorFactory


class ExtendedAuthState(AuthState):
    endpoints: List[str] = Field(default_factory=list)


class AuthManager:
    def __init__(self, config: Configuration, context_name: Optional[str] = None):
        self._logger = get_logger(type(self).__name__)
        self._config = config
        self._context_name = context_name
        self.__events = EventSource(['auth-begin',
                                     'auth-end',
                                     'revoke-begin',
                                     'revoke-end', ])

    @property
    def events(self):
        return self.__events

    def revoke(self, endpoint_ids: List[str], confirmation_operation: Optional[Callable[[], bool]] = None) -> List[str]:
        states = list(self.get_states(endpoint_ids))
        authenticators = self.get_authenticators(endpoint_ids)

        endpoint_ids_with_access_removed: List[str] = []
        index = 0
        total = len(authenticators)

        for authenticator in authenticators:
            state = [s for s in states if s.id == authenticator.session_id][0]
            status = state.status

            affected_endpoint_ids = [
                f'{endpoint_id} (requested)' if endpoint_id in endpoint_ids else endpoint_id
                for endpoint_id in state.endpoints
            ]

            granted_scopes = []
            if state.session_info and state.session_info.get('scope'):
                granted_scopes.extend(sorted(str(state.session_info.get('scope')).split(r' ')))

            basic_event_info = dict(session_id=authenticator.session_id,
                                    index=index,
                                    total=total,
                                    state=state,
                                    endpoint_ids=affected_endpoint_ids,
                                    scopes=granted_scopes)

            self.events.dispatch('revoke-begin', basic_event_info)

            if status == AuthStateStatus.UNINITIALIZED:
                self.events.dispatch('revoke-end', dict(result='already removed', **basic_event_info))
                continue

            if status == AuthStateStatus.REAUTH_REQUIRED or confirmation_operation is None or confirmation_operation():
                authenticator.revoke()
                self.events.dispatch('revoke-end', dict(result='removed', **basic_event_info))
                endpoint_ids_with_access_removed.extend(affected_endpoint_ids)
            else:
                self.events.dispatch('revoke-end', dict(result='aborted', **basic_event_info))
                continue

        return endpoint_ids_with_access_removed

    def get_states(self, endpoint_ids: List[str] = None) -> Iterator[ExtendedAuthState]:
        endpoints = self.get_filtered_endpoints(endpoint_ids)
        for authenticator in self.get_authenticators(endpoint_ids):
            auth_state = authenticator.get_state()
            state = ExtendedAuthState(**auth_state.dict())

            # Simplify the auth info.
            simplified_auth_info = self._remove_none_entry_from(auth_state.auth_info)

            # When type is omitted, the type is default to 'oauth2'. This is required for session-endpoint matching.
            if not simplified_auth_info.get('type'):
                simplified_auth_info['type'] = 'oauth2'

            # Compute the session hash.
            current_hash = JsonModelMixin.hash(simplified_auth_info)

            # Retrieve the associated endpoints.
            for endpoint in endpoints:
                for auth_info in endpoint.get_authentications():
                    # When type is omitted, the type is default to 'oauth2'.
                    if not auth_info.get('type'):
                        auth_info['type'] = 'oauth2'

                    # Compute reference hash
                    ref_hash = JsonModelMixin.hash(self._remove_none_entry_from(auth_info))

                    if ref_hash == current_hash:
                        state.endpoints.append(endpoint.id)

            yield state

    def _remove_none_entry_from(self, d: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in d.items()
            if v is not None
        }

    def initiate_authentications(self, endpoint_ids: List[str] = None, revoke_existing: bool = False):
        authenticators = self.get_authenticators(endpoint_ids)

        index = 0
        total = len(authenticators)

        for authenticator in authenticators:
            state = authenticator.get_state()
            basic_event_info = dict(session_id=authenticator.session_id, state=state, index=index, total=total)

            self.events.dispatch('auth-begin', basic_event_info)

            if state.status == AuthStateStatus.READY:
                # click.secho('>>> Already authenticated\n', dim=True)
                self.events.dispatch('auth-end', basic_event_info)
                continue

            if revoke_existing:
                authenticator.revoke()

            authenticator.initialize()
            state.status = AuthStateStatus.READY
            self.events.dispatch('auth-end', basic_event_info)

            index += 1

    def get_authenticators(self, endpoint_ids: List[str] = None) -> List[Authenticator]:
        filtered_endpoints = self.get_filtered_endpoints(endpoint_ids)
        self._logger.debug(f'get_authenticators({endpoint_ids}): filtered_endpoints = {filtered_endpoints}')
        return HttpAuthenticatorFactory.create_multiple_from(endpoints=filtered_endpoints)

    def get_filtered_endpoints(self, endpoint_ids: List[str] = None) -> List[ServiceEndpoint]:
        wrapper = ConfigurationWrapper(self._config, self._context_name)
        return [
            endpoint
            for endpoint in wrapper.endpoints
            if not endpoint_ids or endpoint.id in endpoint_ids
        ]
