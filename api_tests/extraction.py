import yaml
import json
import requests
from .models import TestExecution

def parse_swagger_yaml(file_path):
    with open(file_path, 'r') as file:
        swagger_data = yaml.safe_load(file)
    base_url = get_base_url(swagger_data)
    save_base_url_to_db(base_url)
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
    base_url = get_base_url(swagger_data)
    save_base_url_to_db(base_url)
    return swagger_data

def get_base_url(swagger_data):
    return swagger_data.get('servers', [{}])[0].get('url', '').rstrip('/')

def save_base_url_to_db(base_url):
    try:
        test_execution = TestExecution.objects.latest('created_at')
        test_execution.base_url = base_url
        test_execution.save()
    except TestExecution.DoesNotExist:
        # Handle the case where no TestExecution exists
        pass