from typing import List

from dnastack.common.environments import flag, env
from tests.cli.auth_utils import handle_device_code_flow
from tests.cli.base import CliTestCase


class TestCommand(CliTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.prepare_for_device_code_flow()

        self.assertEqual(0, len(self._get_context_names()),
                         'There should be no contexts when the test starts.')

    def test_crud(self):
        self.invoke('config', 'contexts', 'add', 'test-context')
        self.assertIn('test-context', self._get_context_names())

        self.invoke('config', 'contexts', 'add', 'test-context-002')
        self.assertIn('test-context-002', self._get_context_names())
        self.assertIn('test-context', self._get_context_names(), 'The previously added context should be there.')

        self.invoke('config', 'contexts', 'rename', 'test-context', 'test-context-001')
        self.assertNotIn('test-context', self._get_context_names(), 'The old context name should not be listed.')
        self.assertIn('test-context-001', self._get_context_names(), 'The new context name should be listed.')
        self.assertIn('test-context-002', self._get_context_names(), 'The previously added context should be there.')

        self.invoke('config', 'contexts', 'remove', 'test-context-002')
        self.assertIn('test-context-001', self._get_context_names(), 'The non-target context should be listed')
        self.assertNotIn('test-context-002', self._get_context_names(), 'The target context should not be listed')

    def test_use_command_with_auth_enabled_on_context_switch(self):
        handle_device_code_flow(['python', '-m', 'dnastack', 'use', '--name', 'test-viral-ai', 'viral.ai'],
                                self._email,
                                self._token)
        self.assertEqual(len(self._get_context_names()), 1, 'There should be ONE context.')
        config = self._load_configuration()
        self.assertEqual(config.current_context, 'test-viral-ai')
        self.assertGreater(len(config.contexts[config.current_context].endpoints), 0,
                           'There should be at least one endpoints.')
        # ↓ This line should not throw an error or prompt for the authentication.
        self.simple_invoke('collections', 'list')

        handle_device_code_flow(['python', '-m', 'dnastack', 'use', 'collection-service.prod.dnastack.com'],
                                self._email,
                                self._token)
        self.assertEqual(len(self._get_context_names()), 2, 'There should be TWO contexts.')
        config = self._load_configuration()
        self.assertEqual(config.current_context, 'collection-service.prod.dnastack.com')
        self.assertGreater(len(config.contexts[config.current_context].endpoints), 0,
                           'There should be at least one endpoints.')
        # ↓ This line should not throw an error or prompt for the authentication.
        self.invoke('collections', 'list', bypass_error=False)

        # Switch the context back should not be a problem.
        self.invoke('use', 'test-viral-ai', bypass_error=False)
        config = self._load_configuration()
        self.assertEqual(config.current_context, 'test-viral-ai')

    def test_use_command_with_auth_disabled_on_context_switch(self):
        # Switching to use the viral.ai context in this scenario should not prompt for the authentication.

        # The test will fail if the line below get timeout.
        self.invoke('use', 'viral.ai', '--no-auth', timeout=30, bypass_error=False)
        self.assertEqual(len(self._get_context_names()), 1, 'There should be ONE context.')
        config = self._load_configuration()
        self.assertEqual(config.current_context, 'viral.ai')
        self.assertGreater(len(config.contexts[config.current_context].endpoints), 0,
                           'There should be at least one endpoints.')
        # ↓ This line should not throw an error or prompt for the authentication.
        handle_device_code_flow(['python', '-m', 'dnastack', 'collections', 'list'], self._email, self._token)
        # self._show_config()

    def test_use_command_with_exact_url(self):
        self.invoke('use', 'https://viral.ai/api/service-registry', '--no-auth', timeout=30, bypass_error=False)
        self.assertEqual(len(self._get_context_names()), 1, 'There should be ONE context.')
        config = self._load_configuration()
        self.assertEqual(config.current_context, 'viral.ai')
        self.assertGreater(len(config.contexts[config.current_context].endpoints), 0,
                           'There should be at least one endpoints.')
        # ↓ This line should not throw an error or prompt for the authentication.
        handle_device_code_flow(['python', '-m', 'dnastack', 'collections', 'list'], self._email, self._token)
        # self._show_config()

    def test_use_command_error_recovery(self):
        # As described in #182492526
        result = self.invoke('use', 'https://viral.ai/api', '--no-auth', timeout=30, bypass_error=True)
        self.assertNotEqual(result.exit_code, 0,
                            'This should not return exit code 0, i.e., the command ran successfully.')
        result = self.invoke('use', 'https://viral.ai/api/service-registry', '--no-auth', timeout=30, bypass_error=False)
        self.assertEqual(result.exit_code, 0,
                            'This should not return exit code 0, i.e., the command ran successfully.')

    def show_output(self) -> bool:
        return False

    def _get_context_names(self) -> List[str]:
        return self.simple_invoke('config', 'contexts', 'list')
