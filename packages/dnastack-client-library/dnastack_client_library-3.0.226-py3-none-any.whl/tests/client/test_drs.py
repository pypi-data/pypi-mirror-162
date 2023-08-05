import os
import re
from typing import Dict
from urllib.parse import urlparse

from dnastack import DataConnectClient
from dnastack.client.collections.client import CollectionServiceClient, STANDARD_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.client.drs import DrsClient, DrsApiError, Blob, DRSDownloadException
from dnastack.common.environments import env
from ..exam_helper import initialize_test_endpoint, BaseTestCase


class TestDrsClient(BaseTestCase):
    """ Test a client for DRS service"""

    # Test-specified
    sample_size = 10
    max_sample_checks = 3

    # Set up the client for the collection service
    collection_endpoint = initialize_test_endpoint(env('E2E_COLLECTION_SERVICE_URL',
                                                       default='https://collection-service.viral.ai/'),
                                                   type=STANDARD_COLLECTION_SERVICE_TYPE_V1_0)
    collection_client = CollectionServiceClient.make(collection_endpoint)

    # Set up the client for the data repository service
    # NOTE: We use the collection service for this test as the service implements DRS interfaces.
    drs_endpoint = initialize_test_endpoint(env('E2E_DRS_URL',
                                                default='https://collection-service.viral.ai/'),
                                            type=DrsClient.get_default_service_type())
    drs_client = DrsClient.make(drs_endpoint)

    def setUp(self):
        super(TestDrsClient, self).setUp()
        self.output_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self) -> None:
        super(TestDrsClient, self).tearDown()
        for file_name in os.listdir(self.output_dir):
            if file_name[0] == '.':
                continue
            os.unlink(os.path.join(self.output_dir, file_name))

    def test_with_blob_using_implicit_arguments(self):
        re_table_type = re.compile(r"type\s*=\s*'blob'")

        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()
        self.assert_not_empty(collections)

        target_collection = [c for c in collections if re_table_type.search(c.itemsQuery)][0]

        items = [
            item
            for item in DataConnectClient.make(collection_client.data_connect_endpoint()) \
                .query(f'{target_collection.itemsQuery} LIMIT {self.sample_size}')
        ]
        self.assert_not_empty(items)

        # Define the test DRS URL
        drs_net_location = urlparse(self.drs_endpoint.url).netloc
        drs_ids = []
        drs_urls = []
        for item in items:
            item_id = item['id']
            item_url = f'drs://{drs_net_location}/{item_id}'
            drs_ids.append(item_id)
            drs_urls.append(item_url)

        errors: Dict[str, Exception] = dict()

        # Download with IDs
        drs_id_to_blob_map: Dict[str, Blob] = dict()
        for drs_id in drs_ids:
            try:
                blob = drs_id_to_blob_map[drs_id] = self.drs_client.get_blob(drs_id)
                self.assertEqual(blob.drs_object.id, drs_id)
                self.assertGreater(len(blob.data), 0)
                blob.close()
            except DrsApiError as e:
                errors[drs_id] = e

            if len(drs_id_to_blob_map) >= self.max_sample_checks:
                break

        if len(errors) == len(drs_ids):
            for drs_id, e in errors.items():
                self._logger.error(f'Failed to download B/{drs_id} ({e})')
            self.fail('All expected samples fail')

        errors.clear()

        # Download with URLs
        drs_url_to_blob_map: Dict[str, Blob] = dict()
        for drs_url in drs_urls:
            try:
                blob = drs_url_to_blob_map[drs_url] = self.drs_client.get_blob(drs_url)
                self.assertEqual(blob.drs_url, drs_url)
                self.assertGreater(len(blob.data), 0)
                blob.close()
            except DrsApiError as e:
                errors[drs_url] = e

            if len(drs_url_to_blob_map) >= self.max_sample_checks:
                break

        if len(errors) == len(drs_ids):
            for drs_id, e in errors.items():
                self._logger.error(f'Failed to download B/{drs_id} ({e})')
            self.fail('All expected samples fail')

        # At this point, getting the blobs either by IDs or URLs should yield the same result.
        self.assertEqual(len(drs_id_to_blob_map), len(drs_url_to_blob_map),
                         'The number of accessible objects should be the same for both approaches.')
        for drs_id, blob_by_id in drs_id_to_blob_map.items():
            try:
                blob_by_url = drs_url_to_blob_map[blob_by_id.drs_url]
                self.assertEqual(drs_id, blob_by_id.drs_object.id)
                self.assertEqual(drs_id, blob_by_url.drs_object.id)
                self.assertEqual(blob_by_id.drs_url, blob_by_url.drs_url)
                self.assertEqual(blob_by_id.drs_object.id, blob_by_url.drs_object.id)
                self.assertEqual(blob_by_id.drs_object.name, blob_by_url.drs_object.name)
            except DrsApiError:
                pass

    def test_with_blob_using_explicit_arguments(self):
        re_table_type = re.compile(r"type\s*=\s*'blob'")

        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()
        self.assert_not_empty(collections)

        target_collection = [c for c in collections if re_table_type.search(c.itemsQuery)][0]

        items = [
            item
            for item in DataConnectClient.make(collection_client.data_connect_endpoint()) \
                .query(f'{target_collection.itemsQuery} LIMIT {self.sample_size}')
        ]
        self.assert_not_empty(items)

        # Define the test DRS URL
        drs_net_location = urlparse(self.drs_endpoint.url).netloc
        drs_ids = []
        drs_urls = []
        for item in items:
            item_id = item['id']
            item_url = f'drs://{drs_net_location}/{item_id}'
            drs_ids.append(item_id)
            drs_urls.append(item_url)

        errors: Dict[str, Exception] = dict()

        # Download with IDs
        drs_id_to_blob_map: Dict[str, Blob] = dict()
        for drs_id in drs_ids:
            try:
                blob = drs_id_to_blob_map[drs_id] = self.drs_client.get_blob(id=drs_id)
                self.assertEqual(blob.drs_object.id, drs_id)
                self.assertGreater(len(blob.data), 0)
                blob.close()
            except DrsApiError as e:
                errors[drs_id] = e

            if len(drs_id_to_blob_map) >= self.max_sample_checks:
                break

        if len(errors) == len(drs_ids):
            for drs_id, e in errors.items():
                self._logger.error(f'Failed to download B/{drs_id} ({e})')
            self.fail('All expected samples fail')

        errors.clear()

        # Download with URLs
        drs_url_to_blob_map: Dict[str, Blob] = dict()
        for drs_url in drs_urls:
            try:
                blob = drs_url_to_blob_map[drs_url] = self.drs_client.get_blob(url=drs_url)
                self.assertEqual(blob.drs_url, drs_url)
                self.assertGreater(len(blob.data), 0)
                blob.close()
            except DrsApiError as e:
                errors[drs_url] = e

            if len(drs_url_to_blob_map) >= self.max_sample_checks:
                break

        if len(errors) == len(drs_ids):
            for drs_id, e in errors.items():
                self._logger.error(f'Failed to download B/{drs_id} ({e})')
            self.fail('All expected samples fail')

        # At this point, getting the blobs either by IDs or URLs should yield the same result.
        self.assertEqual(len(drs_id_to_blob_map), len(drs_url_to_blob_map),
                         'The number of accessible objects should be the same for both approaches.')
        for drs_id, blob_by_id in drs_id_to_blob_map.items():
            try:
                blob_by_url = drs_url_to_blob_map[blob_by_id.drs_url]
                self.assertEqual(drs_id, blob_by_id.drs_object.id)
                self.assertEqual(drs_id, blob_by_url.drs_object.id)
                self.assertEqual(blob_by_id.drs_url, blob_by_url.drs_url)
                self.assertEqual(blob_by_id.drs_object.id, blob_by_url.drs_object.id)
                self.assertEqual(blob_by_id.drs_object.name, blob_by_url.drs_object.name)
            except DrsApiError:
                pass

    def test_download_files(self):
        re_table_type = re.compile(r"type\s*=\s*'blob'")

        collection_client = CollectionServiceClient.make(self.collection_endpoint)

        collections = collection_client.list_collections()
        self.assert_not_empty(collections)

        target_collection = [c for c in collections if re_table_type.search(c.itemsQuery)][0]

        items = [
            item
            for item in DataConnectClient.make(collection_client.data_connect_endpoint()) \
                .query(f'{target_collection.itemsQuery} LIMIT {self.sample_size}')
        ]
        self.assert_not_empty(items)

        # Define the test DRS URL
        drs_net_location = urlparse(self.drs_endpoint.url).netloc
        drs_urls = []
        expected_file_names = set()
        for item in items:
            item_id = item['id']
            expected_file_names.add(os.path.basename(item['name']))
            drs_urls.append(f'drs://{drs_net_location}/{item_id}')

        # Attempt to download the data.
        self.drs_client._download_files(id_or_urls=drs_urls, output_dir=self.output_dir)

        existing_file_names = os.listdir(self.output_dir)
        self.assertGreater(len(existing_file_names), 0)

    def test_downloading_files_with_invalid_urls_raises_error(self):
        drs_net_location = urlparse(self.drs_endpoint.url).netloc

        with self.assertRaises(DRSDownloadException):
            self.drs_client._download_files(id_or_urls=[f'drs://{drs_net_location}/foo-bar'])

        with self.assertRaises(DRSDownloadException):
            self.drs_client._download_files(id_or_urls=[f'drs://shiroyuki.com/foo-bar'])

        with self.assertRaises(DRSDownloadException):
            self.drs_client._download_files(id_or_urls=[f'drs://red-panda.dnastack.com/foo-bar'])
