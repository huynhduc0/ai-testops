import yaml
import json
import requests
from .models import TestExecution
from urllib.parse import urljoin, urlparse
import pytest
from unittest.mock import patch, mock_open

def parse_swagger_yaml(file_path):
    with open(file_path, 'r') as file:
        swagger_data = yaml.safe_load(file)
    return swagger_data

def parse_swagger_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type')
    if 'yaml' in content_type or 'yml' in url:
        swagger_data = yaml.safe_load(response.text)
    elif 'json' in content_type or 'json' in url:
        swagger_data = response.json()
    else:
        raise ValueError("Unsupported Swagger format. Only YAML and JSON are supported.")
    return swagger_data

def get_base_url(swagger_url):
    parsed_url = urlparse(swagger_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {swagger_url}")

    base_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", parsed_url.path.rsplit('/', 1)[0] + '/')
    return base_url

def test_parse_swagger_yaml():
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

@patch("requests.get")
def test_parse_swagger_from_url_yaml(mock_get):
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
def test_parse_swagger_from_url_json(mock_get):
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

def test_get_base_url():
    url = "http://example.com/api/swagger.yaml"
    result = get_base_url(url)
    assert result == "http://example.com/api/"