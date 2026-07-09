import pytest

@pytest.fixture(scope="session")
def iris_base_url() -> str:
    return "http://localhost:52773"

@pytest.fixture(scope="session")
def iris_credentials():
    return (
        "IRIS_USER",
        "IRIS_PASSWORD",
    )