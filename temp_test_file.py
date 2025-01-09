
import requests
import pytest

def test_get_user_user1():
    url = "https://petstore.swagger.io/v2/user/user1"
    try:
        response = requests.get(url)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["username"] == "user1"

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

def test_get_user_nonexistent():
    url = "https://petstore.swagger.io/v2/user/nonexistentuser"
    try:
        response = requests.get(url)
        assert response.status_code == 404
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")

def test_get_user_empty_path():
    url = "https://petstore.swagger.io/v2/user/"
    try:
        response = requests.get(url)
        assert response.status_code == 404

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Request failed: {e}")


