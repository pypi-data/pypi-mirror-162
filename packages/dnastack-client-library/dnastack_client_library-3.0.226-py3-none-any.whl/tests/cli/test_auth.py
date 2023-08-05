from selenium import webdriver
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from subprocess import Popen, PIPE
from time import sleep
from traceback import print_exc

from dnastack.common.environments import env, flag
from .auth_utils import handle_device_code_flow
from .base import CliTestCase
from ..exam_helper import client_id, client_secret, token_endpoint, authorization_endpoint, personal_access_endpoint, \
    redirect_url, device_code_endpoint


class TestAuthentication(CliTestCase):
    # re_url = re.compile(r'https://[^\s]+/authorize\?user_code=[^\s]+')
    test_resource_id = 'test-data-connect'
    test_resource_url = env('E2E_DATA_CONNECT_URL',
                            default='https://collection-service.viral.ai/data-connect/')

    def setUp(self) -> None:
        super().setUp()
        self._add_endpoint(self.test_resource_id, 'data_connect', self.test_resource_url)

    def test_client_credentials_flow(self):
        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.client_id': client_id,
                'authentication.client_secret': client_secret,
                'authentication.grant_type': 'client_credentials',
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint,
            }
        )

        result = self.invoke('auth', 'login')
        self.assertEqual(0, result.exit_code, 'Logging into all endpoints should also work.')

        auth_state = self._get_auth_state_for(self.test_resource_id)
        self.assertEqual(auth_state['status'], 'ready', 'The authenticator should be ready to use.')
        self.assertEqual(auth_state['auth_info']['resource_url'], self.test_resource_url,
                         'The resource URL should be the same as the test resource URL.')

        result = self.invoke('auth', 'revoke', '--force')
        self.assertEqual(0, result.exit_code, 'Revoking all sessions should also work.')

        auth_state = self._get_auth_state_for(self.test_resource_id)
        self.assertEqual(auth_state['status'], 'uninitialized', 'The authenticator should be NOT ready to use.')
        self.assertEqual(auth_state['auth_info']['resource_url'], self.test_resource_url,
                         'The resource URL should be the same as the test resource URL.')

        result = self.invoke('auth', 'login', '--endpoint-id', self.test_resource_id)
        self.assertEqual(0, result.exit_code, 'The login command with a single endpoint should also work.')

        auth_state = self._get_auth_state_for(self.test_resource_id)
        self.assertEqual(auth_state['status'], 'ready', 'The authenticator should be ready to use.')
        self.assertEqual(auth_state['auth_info']['resource_url'], self.test_resource_url,
                         'The resource URL should be the same as the test resource URL.')

        result = self.invoke('auth', 'revoke', '--force', '--endpoint-id', self.test_resource_id)
        self.assertEqual(0, result.exit_code, 'Revoking one session related to the test resource should also work.')

        auth_state = self._get_auth_state_for(self.test_resource_id)
        self.assertEqual(auth_state['status'], 'uninitialized', 'The authenticator should be NOT ready to use.')
        self.assertEqual(auth_state['auth_info']['resource_url'], self.test_resource_url,
                         'The resource URL should be the same as the test resource URL.')

    def _get_auth_state_for(self, endpoint_id: str):
        result = self.simple_invoke('auth', 'status')
        for state in result:
            self.assert_not_empty(state['endpoints'], 'There should be at least one endpoints.')

        try:
            return [state for state in result if endpoint_id in state['endpoints']][0]
        except (KeyError, IndexError):
            raise RuntimeError('Unable to get the state of the authenticator for the test resource')

    def test_personal_access_token_flow(self):
        if flag('`E2E_WEBDRIVER_TESTS_DISABLED`'):
            self.skipTest('All webdriver-related tests as disabled with E2E_WEBDRIVER_TESTS_DISABLED.')

        email = env('E2E_AUTH_PAT_TEST_EMAIL')
        token = env('E2E_AUTH_PAT_TEST_TOKEN')

        if not email or not token:
            self.skipTest('The PAT flow test does not have both email (E2E_AUTH_PAT_TEST_EMAIL) and personal access '
                          'token (E2E_AUTH_PAT_TEST_TOKEN).')

        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.authorization_endpoint': authorization_endpoint,
                'authentication.client_id': client_id,
                'authentication.client_secret': client_secret,
                'authentication.grant_type': 'authorization_code',
                'authentication.personal_access_endpoint': personal_access_endpoint,
                'authentication.personal_access_email': email,
                'authentication.personal_access_token': token,
                'authentication.redirect_url': redirect_url,
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint
            }
        )

        result = self.invoke('auth', 'login', '--endpoint-id', self.test_resource_id)
        self.assertEqual(0, result.exit_code)

    def test_device_code_flow(self):
        self.prepare_for_device_code_flow()

        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.client_id': client_id,
                'authentication.device_code_endpoint': device_code_endpoint,
                'authentication.grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'authentication.redirect_url': redirect_url,
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint
            }
        )

        self._logger.debug('Initiating the auth command in a different process...')

        auth_cmd = ['python', '-m', 'dnastack', 'auth', 'login']
        handle_device_code_flow(auth_cmd, self._email, self._token)
