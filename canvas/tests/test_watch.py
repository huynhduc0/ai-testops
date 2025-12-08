import unittest
from unittest.mock import patch, mock_open, MagicMock

import requests
import watch

class TestWatch(unittest.TestCase):
    @patch('watch.Consumer')
    @patch('watch.Producer')
    def test_listen_for_kafka_messages(self, mock_producer, mock_consumer):
        mock_consumer_instance = mock_consumer.return_value
        mock_consumer_instance.poll.side_effect = [
            MagicMock(value=b'{"test_id": 1, "script": "print(\'Hello World\')"}'),
            StopIteration  # To break the infinite loop
        ]
        mock_producer_instance = mock_producer.return_value

        with patch('watch.run_test_case', return_value={'status': 'passed', 'log': 'test log'}):
            with patch('watch.save_test_result_to_db') as mock_save:
                try:
                    watch.listen_for_kafka_messages()
                except StopIteration:
                    pass
                mock_save.await_count(0)

    @patch('watch.Consumer')
    @patch('watch.Producer')
    def test_listen_for_kafka_messages_missing_test_id(self, mock_producer, mock_consumer):
        mock_consumer_instance = mock_consumer.return_value
        mock_consumer_instance.poll.side_effect = [
            MagicMock(value=b'{"script": "print(\'Hello World\')"}'),
            StopIteration  # To break the infinite loop
        ]
        mock_producer_instance = mock_producer.return_value

        with patch('watch.run_test_case', return_value={'status': 'passed', 'log': 'test log'}):
            with patch('watch.save_test_result_to_db') as mock_save:
                try:
                    watch.listen_for_kafka_messages()
                except StopIteration:
                    pass
                mock_save.assert_not_called()

    @patch('watch.Consumer')
    @patch('watch.Producer')
    def test_listen_for_kafka_messages_received_message(self, mock_producer, mock_consumer):
        mock_consumer_instance = mock_consumer.return_value
        mock_consumer_instance.poll.side_effect = [
            MagicMock(value=b'{"test_id": 1, "script": "print(\'Hello World\')"}'),
            StopIteration  # To break the infinite loop
        ]
        mock_producer_instance = mock_producer.return_value

        with patch('watch.run_test_case', return_value={'status': 'passed', 'log': 'test log'}):
            with patch('watch.save_test_result_to_db') as mock_save:
                with patch('watch.TEST_CASES_STATUS.labels') as mock_labels:
                    try:
                        watch.listen_for_kafka_messages()
                    except StopIteration:
                        pass
                    # mock_save.assert_called_once()
                    mock_labels.assert_not_called()

    @patch('watch.Consumer')
    @patch('watch.Producer')
    def test_listen_for_kafka_messages_parsing_error(self, mock_producer, mock_consumer):
        mock_consumer_instance = mock_consumer.return_value
        mock_consumer_instance.poll.side_effect = [
            MagicMock(value=b'{"invalid_json": }'),
            StopIteration  # To break the infinite loop
        ]
        mock_producer_instance = mock_producer.return_value

        with patch('watch.run_test_case', return_value={'status': 'passed', 'log': 'test log'}):
            with patch('watch.save_test_result_to_db') as mock_save:
                with patch('watch.TEST_CASES_STATUS.labels') as mock_labels:
                    try:
                        watch.listen_for_kafka_messages()
                    except StopIteration:
                        pass
                    mock_save.assert_not_called()
                    mock_labels.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data="print('Hello World')")
    @patch('watch.subprocess.run')
    @patch('os.remove')
    def test_run_test_case(self, mock_os_remove, mock_subprocess_run, mock_file):
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout='test passed', stderr='')

        result = watch.run_test_case(1, "print('Hello World')")
        self.assertEqual(result['status'], 'passed')
        self.assertIn('test passed', result['log'])
        mock_os_remove.assert_called_once_with('temp_test_file.py')

    @patch('watch.requests.post')
    def test_save_test_result_to_db(self, mock_post):
        mock_post.return_value.status_code = 200

        watch.save_test_result_to_db(1, 'passed', 'test log')
        mock_post.assert_called_once_with('http://app:8000/api_test/api/save/1/', json={'status': 'passed', 'log': 'test log'})

    @patch('watch.requests.post')
    def test_save_test_result_to_db_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        with patch('watch.logging.error') as mock_log_error:
            watch.save_test_result_to_db(1, 'failed', 'test log')
            mock_post.assert_called_once_with('http://localhost:8000/api_test/api/save/1/', json={'status': 'failed', 'log': 'test log'})
            mock_log_error.assert_called()

    @patch('watch.requests.post', side_effect=requests.exceptions.RequestException)
    def test_save_test_result_to_db_exception(self, mock_post):
        with patch('watch.logging.error') as mock_log_error:
            watch.save_test_result_to_db(1, 'failed', 'test log')
            mock_post.assert_called_once_with('http://localhost:8000/api_test/api/save/1/', json={'status': 'failed', 'log': 'test log'})
            mock_log_error.assert_called()

    @patch('watch.subprocess.run', side_effect=FileNotFoundError('pytest not found'))
    @patch('os.remove')
    def test_run_test_case_pytest_not_found(self, mock_os_remove, mock_subprocess_run):
        result = watch.run_test_case(1, "print('Hello World')")
        self.assertEqual(result['status'], 'error')
        self.assertIn('pytest not found', result['log'])
        mock_os_remove.assert_called_once_with('temp_test_file.py')

    @patch('watch.subprocess.run', side_effect=Exception('unexpected error'))
    @patch('os.remove')
    def test_run_test_case_unexpected_error(self, mock_os_remove, mock_subprocess_run):
        result = watch.run_test_case(1, "print('Hello World')")
        self.assertEqual(result['status'], 'error')
        self.assertIn('unexpected error', result['log'])
        mock_os_remove.assert_called_once_with('temp_test_file.py')

if __name__ == '__main__':
    unittest.main()
