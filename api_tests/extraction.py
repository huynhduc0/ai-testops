import yaml
import json
import requests
from .models import TestExecution
from urllib.parse import urljoin, urlparse

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