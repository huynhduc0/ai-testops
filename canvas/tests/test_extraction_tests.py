import unittest
import pytest
from unittest.mock import patch, mock_open
from api_tests.extraction import parse_swagger_yaml, parse_swagger_from_url, get_base_url

class TestExtraction(unittest.TestCase):
    def test_parse_swagger_yaml(self):
        yaml_content = """
        openapi: 3.0.0
        info:
          title: Sample API
          version: 0.1.0
        paths:
          /test:
            get:
              summary: Test endpoint
        """
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = parse_swagger_yaml("dummy_path.yaml")
            assert result["openapi"] == "3.0.0"
            assert "/test" in result["paths"]

    def test_parse_swagger_yaml_invalid_file(self):
        with pytest.raises(FileNotFoundError):
            parse_swagger_yaml("non_existent_file.yaml")

    @patch("requests.get")
    def test_parse_swagger_from_url_yaml(self, mock_get):
        yaml_content = """
        openapi: 3.0.0
        info:
          title: Sample API
          version: 0.1.0
        paths:
          /test:
            get:
              summary: Test endpoint
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "application/x-yaml"}
        mock_get.return_value.text = yaml_content
        result = parse_swagger_from_url("http://example.com/swagger.yaml")
        assert result["openapi"] == "3.0.0"
        assert "/test" in result["paths"]

    @patch("requests.get")
    def test_parse_swagger_from_url_json(self, mock_get):
        json_content = {
            "openapi": "3.0.0",
            "info": {
                "title": "Sample API",
                "version": "0.1.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint"
                    }
                }
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "application/json"}
        mock_get.return_value.json.return_value = json_content
        result = parse_swagger_from_url("http://example.com/swagger.json")
        assert result["openapi"] == "3.0.0"
        assert "/test" in result["paths"]

    @patch("requests.get")
    def test_parse_swagger_from_url_invalid_format(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-Type": "text/plain"}
        mock_get.return_value.text = "Invalid content"
        with pytest.raises(ValueError, match="Unsupported Swagger format. Only YAML and JSON are supported."):
            parse_swagger_from_url("http://example.com/invalid_format.txt")

    def test_get_base_url(self):
        url = "http://example.com/api/swagger.yaml"
        result = get_base_url(url)
        assert result == "http://example.com/api/"

    def test_get_base_url_invalid_url(self):
        with pytest.raises(ValueError, match="Invalid URL: invalid_url"):
            get_base_url("invalid_url")

    def test_get_base_url_no_scheme(self):
        with pytest.raises(ValueError, match="Invalid URL: example.com/api/swagger.yaml"):
            get_base_url("example.com/api/swagger.yaml")

if __name__ == '__main__':
    unittest.main()