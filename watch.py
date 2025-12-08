import logging
from confluent_kafka import Consumer, Producer
import os
import subprocess
import requests
import json
from prometheus_client import start_http_server, Counter

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
PUBLISHER_URL = os.getenv('PUBLISHER_URL', 'http://localhost:8000')
DEAD_LETTER_QUEUE = 'dead_letter_queue'

# Prometheus metrics
TEST_CASES_STATUS = Counter('test_cases_status', 'Status of test cases', ['test_case_id', 'status'])

def listen_for_kafka_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'test_group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,  # Enable auto-commit
        'auto.commit.interval.ms': 5000,  # Commit every 5 seconds
        'max.poll.records': 50,  # Fetch up to 50 messages per poll (3 partitions * ~16-17 per partition)
        'session.timeout.ms': 30000,  # 30s session timeout
        'heartbeat.interval.ms': 10000,  # Send heartbeat every 10s (1/3 of session timeout)
    })
    consumer.subscribe(['test_run_queue'])
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    print("Listening for messages...")
    try:
        while True:
            # Poll with 2.0 second timeout for batching
            msg = consumer.poll(2.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue

            print(f"Received message from partition {msg.partition()}, offset {msg.offset()}: {msg.value().decode('utf-8')}")
            try:
                message = json.loads(msg.value().decode('utf-8'))
                test_case_id = message['test_id']
                test_file_content = message['script']
                result = run_test_case(test_case_id, test_file_content)
                save_test_result_to_db(test_case_id, result['status'], result['log'])
                TEST_CASES_STATUS.labels(test_case_id=test_case_id, status=result['status']).inc()
                # Offset is automatically committed by enable.auto.commit
                print(f"Successfully processed test case {test_case_id}")
            except (json.JSONDecodeError, KeyError) as e:
                TEST_CASES_STATUS.labels(test_case_id=test_case_id, status="error").inc()
                logging.error(f"Error parsing message: {e}")
                producer.produce(DEAD_LETTER_QUEUE, msg.value())
                producer.flush()
                # Still commit offset to avoid reprocessing poison messages
                consumer.commit(asynchronous=True)
    except KeyboardInterrupt:
        pass
    finally:
        # Final commit before closing
        consumer.commit(asynchronous=False)
        consumer.close()

def run_test_case(test_case_id, test_file_content):
    with open('temp_test_file.py', 'w') as f:
        f.write(test_file_content)
    print(f"Running pytest on temp_test_file.py for test case ID {test_case_id}")
    try:
        result = subprocess.run(['pytest', 'temp_test_file.py'], capture_output=True, text=True)
        print(result)
        status = 'passed' if result.returncode == 0 else 'failed'
        return {
            'status': status,
            'log': result.stdout + result.stderr
        }
    except FileNotFoundError as e:
        logging.error(f"Pytest executable not found: {e}")
        return {
            'status': 'error',
            'log': str(e)
        }
    except Exception as e:
        logging.error(f"Error running pytest: {e}")
        return {
            'status': 'error',
            'log': str(e)
        }
    finally:
        print("Cleaning up temp_test_file.py")
        os.remove('temp_test_file.py')

def save_test_result_to_db(test_case_id, status, log):
    url = f"{PUBLISHER_URL}/api_test/api/save/{test_case_id}/"
    data = {
        'status': status,
        'log': log
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logging.error(f"Failed to save test result: {response.content}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")

def main():
    # Start Prometheus metrics server
    start_http_server(8001)
    listen_for_kafka_messages()

if __name__ == "__main__":
    main()
