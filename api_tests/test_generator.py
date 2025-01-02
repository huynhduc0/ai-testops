# api_tests/test_generator.py
import pytest
import requests
import tempfile
import os

def generate_test_cases(llm, swagger_data):
    test_cases = []
    for path, methods in swagger_data['paths'].items():
        for method, details in methods.items():
            url = path
            method = method.upper()
            body = details.get('requestBody', {})
            parameters = details.get('parameters', [])
            prompt = (
                f"Generate a test case for the {method} {url} endpoint with the following details:\n"
                f"Body: {body}\n"
                f"Parameters: {parameters}\n"
                f"Details: {details}"
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
    return test_cases

def run_test_cases(test_cases):
    results = []
    for test_case in test_cases:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(test_case.encode('utf-8'))
            temp_file.close()
            try:
                result = pytest.main([temp_file.name])
                if result == 0:
                    results.append((test_case, "Passed"))
                else:
                    results.append((test_case, "Failed"))
            except Exception as e:
                results.append((test_case, f"Failed: {e}"))
            finally:
                os.remove(temp_file.name)
    return results

def generate_report(results):
    report = "API Test Report\n\n"
    for test_case, result in results:
        report += f"Test Case:\n{test_case}\nResult: {result}\n\n"
    return report