import pytest
from unittest.mock import patch, MagicMock
from api_tests.test_generator import generate_test_case, generate_test_cases, create_test_case_file, request_run_test_case, generate_report

def test_generate_test_case():
    llm = MagicMock()
    llm.generate_test_case.return_value = "Generated test case content"
    test_case = MagicMock()
    test_case.method = "POST"
    test_case.url = "/api/test"
    test_case.body = "{}"
    test_case.parameters = "{}"
    test_case.content = ""
    base_url = "http://localhost:8000"
    result = generate_test_case(llm, test_case, base_url)
    assert result.content == "Generated test case content"

def test_generate_test_cases():
    llm = MagicMock()
    llm.generate_test_case.return_value = "Generated test case content"
    swagger_data = {
        "paths": {
            "/api/test": {
                "post": {
                    "requestBody": {},
                    "parameters": [],
                    "description": "Test endpoint"
                }
            }
        },
        "servers": [{"url": "http://localhost:8000"}]
    }
    result = generate_test_cases(llm, swagger_data)
    assert len(result) == 1
    assert result[0]['content'] == "Generated test case content"

@patch('builtins.open', new_callable=MagicMock)
@patch('confluent_kafka.Producer')
def test_create_test_case_file(mock_producer, mock_open):
    test_case_content = "Generated test case content"
    test_case_id = 1
    file_path = create_test_case_file(test_case_content, test_case_id)
    mock_open.assert_called_once_with(f"/test_cases/test_case_{test_case_id}.py", 'w')
    mock_producer.return_value.produce.assert_called_once()
    assert file_path == f"/test_cases/test_case_{test_case_id}.py"

def test_request_run_test_case():
    test_case = MagicMock()
    test_case.id = 1
    test_case.content = "Generated test case content"
    with patch('api_tests.test_generator.TestCase.objects.get', return_value=test_case):
        result = request_run_test_case(test_case.id, test_case.content)
        assert result['status'] == 'executed'

def test_generate_report():
    results = [
        {'test_case': 1, 'status': 'executed', 'summary': 'Test executed successfully', 'log': ''},
        {'test_case': 2, 'status': 'failed', 'summary': 'Test failed', 'log': ''}
    ]
    report = generate_report(results)
    assert "Test Execution Report" in report
    assert "Test Case ID: 1" in report
    assert "Status: executed" in report
    assert "Test Case ID: 2" in report
    assert "Status: failed" in report
