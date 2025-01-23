import requests
import tempfile
import os
import logging
from confluent_kafka import Producer
import json
from .models import TestCase, TestResult
from .generators.gemini import GeminiLLM
from .generators.llm_offline import OfflineLLM

logging.basicConfig(level=logging.DEBUG)

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def generate_test_case(llm, test_case, base_url, additional_prompt=''):
    prompt = (
        f"""
        Generate a pytest test case for the following API endpoint:

        Method: {test_case.method}
        URL: {base_url}{test_case.url}
        Body (if applicable): {test_case.body}
        Parameters (if applicable): {test_case.parameters}
        Details/Description: {test_case.content}

        {additional_prompt}

        The test case should:

        *   Use the `requests` library to make the API call.
        *   Include assertions to validate the response status code (e.g., 200, 201, 400, 500).
        *   Include assertions to validate the response body (JSON) against expected values or schema (if available in details).
        *   Be concise and ready to be copied directly into a pytest test file.
        *   Handle potential errors gracefully (e.g., connection errors).
        *   If details provide example response, use it to create assertions.
        *   If no example response is provided, create basic status code check.
        *   Cover boundary tests (e.g., empty input, maximum length input).

        Example of expected output format:

        import requests
        import pytest

        def test_{test_case.method.lower()}_{test_case.url.replace('/', '_').replace('.', '_')}():
            url = "{base_url}{test_case.url}"
            <request_body_variable> # Only if body is provided
            try:
                response = requests.{test_case.method.lower()}(url, <request_body_argument>) # Adjust arguments based on method and body
                assert response.status_code == <expected_status_code> # Replace with expected code
                # Example JSON body assertion (adapt as needed)
                # assert response.json()["some_key"] == "expected_value"
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Request failed: <e>")

        Do not include any explanations or extra text. Only the code.
        """
    )
    test_case.content = llm.generate_test_case(prompt)
    test_case.content = test_case.content.replace("```python", "").replace("```", "")
    test_case.save()
    return test_case

def generate_test_cases(llm, swagger_data):
    test_cases = []
    base_url = swagger_data.get('servers', [{}])[0].get('url', '').rstrip('/')
    for path, methods in swagger_data['paths'].items():
        for method, details in methods.items():
            url = f"{base_url}{path}"
            method = method.upper()
            body = details.get('requestBody', {})
            parameters = details.get('parameters', [])
            prompt = (
                f"""
                Generate a pytest test case for the following API endpoint:

                Method: {method}
                URL: {url}
                Body (if applicable): {body}
                Parameters (if applicable): {parameters}
                Details/Description: {details}

                The test case should:

                *   Use the `requests` library to make the API call.
                *   Include assertions to validate the response status code (e.g., 200, 201, 400, 500).
                *   Include assertions to validate the response body (JSON) against expected values or schema (if available in details).
                *   Be concise and ready to be copied directly into a pytest test file.
                *   Handle potential errors gracefully (e.g., connection errors).
                *   If details provide example response, use it to create assertions.
                *   If no example response is provided, create basic status code check.
                *   Cover boundary tests (e.g., empty input, maximum length input).

                Example of expected output format:

                import requests
                import pytest

                def test_{method.lower()}_{url.replace('/', '_').replace('.', '_')}():
                    url = "{url}"
                    <request_body_variable> # Only if body is provided
                    try:
                        response = requests.{method.lower()}(url, <request_body_argument>) # Adjust arguments based on method and body
                        assert response.status_code == <expected_status_code> # Replace with expected code
                        # Example JSON body assertion (adapt as needed)
                        # assert response.json()["some_key"] == "expected_value"
                    except requests.exceptions.RequestException as e:
                        pytest.fail(f"Request failed: <e>")

                Do not include any explanations or extra text. Only the code.
                """
            )
            test_case_content = llm.generate_test_case(prompt)
            test_case = {
                'url': url,
                'method': method,
                'body': body,
                'parameters': parameters,
                'content': test_case_content
            }
            test_cases.append(test_case)
            print(f"Generated test case for {method} {url} endpoint.")
    return test_cases

def create_test_case_file(test_case_content, test_case_id):
    file_path = f"/test_cases/test_case_{test_case_id}.py"
    with open(file_path, 'w') as file:
        file.write(test_case_content)
    logging.debug(f"Test case file created at {file_path}")

    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    message = json.dumps({'test_id': test_case_id, 'script': test_case_content})
    producer.produce('test_run_queue', message.encode('utf-8'))
    producer.flush()

    return file_path

def request_run_test_case(test_case_id, content):
    # Simulate running the test case
    test_case = TestCase.objects.get(id=test_case_id)
    test_case.status = 'executed'
    test_case.save()
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})
    message = json.dumps({'test_id': test_case_id, 'script': test_case.content})
    producer.produce('test_run_queue', message.encode('utf-8'))
    producer.flush()
    return {'status': 'executed'}

def generate_report(results):
    report = "Test Execution Report\n"
    for result in results:
        report += f"Test Case ID: {result['test_case']}\n"
        report += f"Status: {result['status']}\n"
        report += f"Summary: {result['summary']}\n"
        report += f"Log: {result['log']}\n\n"
    return report
