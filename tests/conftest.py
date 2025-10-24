import pytest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture(scope="session")
def sample_storage_path(tmp_path_factory):
    return tmp_path_factory.mktemp("storage")


@pytest.fixture
def mock_qiniu_storage():
    class MockQiniuStorage:
        def upload(self, file_path, key):
            return f"https://cdn.qiniu.com/{key}"
        
        def download(self, key, local_path):
            return local_path
    
    return MockQiniuStorage()


@pytest.fixture
def mock_redis_cache():
    class MockRedisCache:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
                return True
            return False
    
    return MockRedisCache()


@pytest.fixture
def mock_celery_task():
    class MockCeleryTask:
        def __init__(self):
            self.state = "PENDING"
            self.progress = 0
        
        def update_state(self, state, meta=None):
            self.state = state
            if meta and "progress" in meta:
                self.progress = meta["progress"]
        
        def get_state(self):
            return self.state
    
    return MockCeleryTask()
