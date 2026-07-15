import os
import pytest

@pytest.fixture(scope="session")
def iris_base_url() -> str:
    return os.environ.get("IRIS_BASE_URL", "http://localhost:52773")

@pytest.fixture(scope="session")
def iris_credentials():
    return (os.environ.get("IRISUSERNAME", ""), os.environ.get("IRISPASSWORD", ""))