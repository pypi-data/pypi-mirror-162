from tests.cli.auth_utils import handle_device_code_flow
from tests.cli.base import CliTestCase


class TestSmoke(CliTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.prepare_for_device_code_flow()

    def test_happy_path(self):
        handle_device_code_flow(['python', '-m', 'dnastack', 'use', 'viral.ai'],
                                self._email,
                                self._token)

        for collection in self.simple_invoke('collections', 'list'):
            collection_id = collection['slugName']
            try:
                self.invoke('collections', 'tables', 'list', '--collection', collection_id)
                self.invoke('collections', 'query', '-c', collection_id, 'SELECT 1')
                self.invoke('collections', 'query', '--collection', collection_id, 'SELECT 1')
                return
            except:
                pass

        self.fail('No usable collection for the CLI smoke test')
