import requests
import pytest

from endpoints import ContentType, ENDPOINTS
import warnings

def _id(endpoint):
    return f"{endpoint.method} {endpoint.path}"

def _call(endpoint, base_url, auth=None):
    return requests.request(
        endpoint.method,
        f"{base_url}{endpoint.path}",
        auth=auth,
        # verify=False,     # VM uses a private CA #TODO: fix
        headers=endpoint.headers,
        params=endpoint.params,
        timeout=10,
    )


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=_id)
def test_alive(endpoint, iris_base_url, iris_credentials):
    """test if endpoint is alive and server doesn't error"""
    auth = iris_credentials if endpoint.auth else None
    response = _call(endpoint, iris_base_url, auth)
    assert response.status_code != 404, (
        f"{_id(endpoint)} returned {response.status_code} (endpoint not found)"
    )
    assert response.status_code < 500, (
        f"{_id(endpoint)} returned {response.status_code} (server error)"
    )


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=_id)
def test_authentication(endpoint, iris_base_url):
    """Test if authentication is setup as expected"""
    response = _call(endpoint, iris_base_url, auth=None)

    if endpoint.auth:
        assert response.status_code == 401, (
            f"{_id(endpoint)} is marked auth=True but returned {response.status_code} without credentials (expected 401)"
        )
    else:
        assert response.status_code != 401, (
            f"{_id(endpoint)} is marked auth=False but challenged for credentials (401)"
        )


@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=_id)
def test_wrong_credentials_authentication(endpoint, iris_base_url):
    """test if user validation is setup as expected"""
    response = _call(endpoint, iris_base_url, auth=("fakeUser", "Wrongpassword"))

    if endpoint.auth:
        assert response.status_code == 403, (
            f"{_id(endpoint)} is marked auth=True but returned {response.status_code} with wrong credentials (expected 403)"
        )
    else:
        assert response.status_code != 403, (
            f"{_id(endpoint)} is marked auth=False but challenged for credentials (403)"
        )
    

@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=_id)
def test_body_and_header(endpoint, iris_base_url, iris_credentials):
    """Content-Type header matches the declared kind, and the body parses as
    that kind. Called WITH credentials when needed, to reach the real body."""

    if endpoint.content is ContentType.SKIP:
        pytest.skip("body and header check is turned off for this endpoint")

    auth = iris_credentials if endpoint.auth else None
    response = _call(endpoint, iris_base_url, auth)

    assert response.status_code == 200, "Call did not return 200 so cannot test on result."

    # 1. header check. using in, not equals (because of charset suffixes like '; charset=utf-8')
    actual = response.headers.get("Content-Type", "")
    assert endpoint.content.header_match in actual, (
        f"{_id(endpoint)} expected Content-Type containing "
        f"'{endpoint.content.header_match}', got '{actual}'"
    )

    # 2. body parse. the parser is stored in the enum
    endpoint.content.parser(response)