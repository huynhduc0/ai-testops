import yaml
import json
import requests

def parse_swagger_yaml(file_path):
    with open(file_path, 'r') as file:
        swagger_data = yaml.safe_load(file)
    return swagger_data

def parse_swagger_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type')
    if 'yaml' in content_type or 'yml' in url:
        return yaml.safe_load(response.text)
    elif 'json' in content_type or 'json' in url:
        return response.json()
    else:
        raise ValueError("Unsupported Swagger format. Only YAML and JSON are supported.")

def get_base_url(swagger_data):
    return swagger_data.get('servers', [{}])[0].get('url', '').rstrip('/')