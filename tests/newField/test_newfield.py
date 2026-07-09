import iris

def test_running_in_process():
    version = iris.cls("%SYSTEM.Version").GetVersion()
    assert "IRIS" in version

def test_namespace_context():
    ns = iris.cls("%SYSTEM.Process").NameSpace()
    assert ns  # e.g. "USER"
