import unittest
from unittest.mock import patch, mock_open, MagicMock
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
        mock_post.assert_called_once_with('http://localhost:8000/api_test/save/1/', json={'status': 'passed', 'log': 'test log'})

if __name__ == '__main__':
    unittest.main()
