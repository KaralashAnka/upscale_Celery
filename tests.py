import pytest
import io
import time
from app import app
from tasks import celery_app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upscale_route(client):
    # Create a dummy image
    img_data = io.BytesIO(b"fake image data")
    
    response = client.post('/upscale', data={'file': (img_data, 'test.png')}, content_type='multipart/form-data')
    assert response.status_code == 202
    assert 'task_id' in response.json

def test_status_and_result(client):
    # This test might fail if celery worker is not running, 
    # but we can test the API structure
    img_data = io.BytesIO(open('lama_300px.png', 'rb').read())
    
    post_res = client.post('/upscale', data={'file': (img_data, 'lama_300px.png')}, content_type='multipart/form-data')
    task_id = post_res.json['task_id']
    
    # Poll for completion (in a real test environment we'd use a mock or a local worker)
    timeout = 30
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_res = client.get(f'/tasks/{task_id}')
        assert status_res.status_code == 200
        if status_res.json['status'] == 'SUCCESS':
            break
        time.sleep(1)
    
    if status_res.json['status'] == 'SUCCESS':
        assert 'result' in status_res.json
        processed_url = status_res.json['result']
        # The URL is external, so we extract the path
        path = processed_url.split('5000')[-1]
        file_res = client.get(path)
        assert file_res.status_code == 200
        assert file_res.mimetype == 'image/png'
