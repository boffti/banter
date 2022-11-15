import pytest
from flask import Flask
from app import app

@pytest.fixture
def client():
    # app = Flask(__name__)
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_home(client):
    res = client.get('/')
    assert res.status_code == 200