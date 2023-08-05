import logging
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from os import cpu_count
from threading import Lock, Semaphore

from typing import List, Optional

from dnastack import DataConnectClient
from dnastack.client.data_connect import TableInfo
from dnastack.common.environments import env
from dnastack.common.logger import get_logger
from tests.exam_helper import initialize_test_endpoint


class DataConnectTestCaseMixin:
    _max_approx_usable_table_count = 4
    _usable_table_names: Optional[List[str]] = None

    _table_scanning_network_lock = Semaphore(_max_approx_usable_table_count)
    _table_scanning_sync_lock = Lock()

    _test_data_connect_endpoint = initialize_test_endpoint(
        env('E2E_DATA_CONNECT_URL', default='https://collection-service.viral.ai/data-connect/'),
        type=DataConnectClient.get_default_service_type()
    )

    @property
    def usable_table_names(self) -> List[str]:
        if self._usable_table_names is None:
            self._scan_for_usable_tables()
        return self._usable_table_names

    @staticmethod
    def _scan_for_usable_tables():
        logger = get_logger(f'DataConnectTestCaseMixin/table-scanner', logging.INFO)

        logger.info('Scanning for usable tables')

        client = DataConnectClient.make(DataConnectTestCaseMixin._test_data_connect_endpoint)
        DataConnectTestCaseMixin._usable_table_names = []

        worker_count = min(2, cpu_count() * 2, DataConnectTestCaseMixin._max_approx_usable_table_count)
        futures: List[Future] = list()
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            for target_table in client.list_tables():
                futures.append(
                    pool.submit(DataConnectTestCaseMixin._check_if_table_is_usable,
                                client=client,
                                target_table=target_table)
                )

            DataConnectTestCaseMixin._usable_table_names.extend([
                future.result()
                for future in as_completed(futures)
                if future.result() is not None
            ])

        if not DataConnectTestCaseMixin._usable_table_names:
            raise RuntimeError('No usable tables for any Data Connect tests')

        logger.info('Scanning for usable tables is complete.')

    @staticmethod
    def _check_if_table_is_usable(client: DataConnectClient, target_table: TableInfo):
        max_approx_usable_table_count = DataConnectTestCaseMixin._max_approx_usable_table_count

        with DataConnectTestCaseMixin._table_scanning_network_lock:
            logger = get_logger(f'DataConnectTestCaseMixin/table-checker')
            table = client.table(target_table)

            with DataConnectTestCaseMixin._table_scanning_sync_lock:
                if len(DataConnectTestCaseMixin._usable_table_names) >= max_approx_usable_table_count:
                    return 2  # excluded due to limit

            try:
                table_info = table.info
            except Exception as e:
                logger.info(f'T/{table.name}: Failed to check the info ({type(e).__name__}: {e})')
                return 0  # excluded due to error

            try:
                column_name = list(table_info.data_model.get("properties").keys())[0]
                __ = [row for row in client.query(f'SELECT {column_name} FROM {table.name} LIMIT 1')]
            except Exception as e:
                logger.info(f'T/{table.name}: Failed to check the data access ({type(e).__name__}: {e})')
                return 0  # excluded due to error

            with DataConnectTestCaseMixin._table_scanning_sync_lock:
                if len(DataConnectTestCaseMixin._usable_table_names) >= max_approx_usable_table_count:
                    return 2  # excluded due to limit
                DataConnectTestCaseMixin._usable_table_names.append(table.name)

            return 1  # included
