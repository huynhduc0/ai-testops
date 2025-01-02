import yaml
import requests

def parse_swagger_yaml(file_path):
    with open(file_path, 'r') as file:
        swagger_data = yaml.safe_load(file)
    return swagger_data

def parse_swagger_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return yaml.safe_load(response.text)