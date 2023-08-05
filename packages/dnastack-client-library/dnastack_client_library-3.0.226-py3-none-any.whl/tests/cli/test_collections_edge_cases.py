from uuid import uuid4

from dnastack.client.collections.client import UnknownCollectionError
from tests.cli.auth_utils import handle_device_code_flow
from tests.cli.base import CliTestCase


class TestEndToEnd(CliTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.prepare_for_device_code_flow(email_env_var_name='E2E_STAGING_AUTH_DEVICE_CODE_TEST_EMAIL',
                                          token_env_var_name='E2E_STAGING_AUTH_DEVICE_CODE_TEST_TOKEN')
        handle_device_code_flow(['python', '-m', 'dnastack', 'use', 'explorer.alpha.dnastack.com'],
                                self._email,
                                self._token)

    def test_182678656(self):
        """
        https://www.pivotaltracker.com/story/show/182678656

        When using the "dnastack collections query" command after initializing with the "dnastack use" command,
        there should not be an additional auth prompt if the target per-collection data-connect endpoint is registered.
        """
        self.simple_invoke('collections',
                           'query',
                           '-c', 'explorer-staging-controlled-collection',
                           'SELECT 1')

    def test_182881149(self):
        """
        https://www.pivotaltracker.com/story/show/182881149

        When querying on a non-existing collection, it should fail as the collection does not exist,
        not the authentication error, which is misleading.
        """
        with self.assert_exception_raised_in_chain(UnknownCollectionError):
            self.invoke('collections',
                        'query',
                        '-c', f'foobar-{uuid4()}',
                        'SELECT 1')
