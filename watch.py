import logging
from confluent_kafka import Consumer, Producer
import os
import subprocess
import requests
import json

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
DEAD_LETTER_QUEUE = 'dead_letter_queue'

def listen_for_kafka_messages():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'test_group',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['test_run_queue'])
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    print("Listening for messages...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error(f"Consumer error: {msg.error()}")
                continue

            print(f"Received message: {msg.value().decode('utf-8')}")
            try:
                message = json.loads(msg.value().decode('utf-8'))
                test_case_id = message['test_id']
                test_file_content = message['script']
                result = run_test_case(test_case_id, test_file_content)
                save_test_result_to_db(test_case_id, result['status'], result['log'])
            except (json.JSONDecodeError, KeyError) as e:
                logging.error(f"Error parsing message: {e}")
                producer.produce(DEAD_LETTER_QUEUE, msg.value())
                producer.flush()
    except KeyboardInterrupt:
        pass
    finally:
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
    url = f"http://app:8000/api_test/api/save/{test_case_id}/"
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
    listen_for_kafka_messages()

if __name__ == "__main__":
    main()
