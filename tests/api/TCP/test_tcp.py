import socket
import pytest

TCP_ENDPOINTS = [
    ("hl7-adt", 2575),
    ("health", 9000),
]

def _tcp_id(endpoint):
    """returns the id for this specific endpoint so it can be used to identify which endpoint was used on which test"""
    return f"TCP {endpoint[0]}:{endpoint[1]}"

@pytest.mark.parametrize("endpoint", TCP_ENDPOINTS, ids=_tcp_id)
def test_tcp_alive(endpoint):
    """test if TCP port accepts connections"""
    name, port = endpoint
    try:
        with socket.create_connection(("localhost", port), timeout=5):
            pass  # connection succeeded = alive
    except (ConnectionRefusedError, socket.timeout) as e:
        pytest.fail(f"{name}:{port} not reachable ({e})")