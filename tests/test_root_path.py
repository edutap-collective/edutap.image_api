"""The service must answer under the path prefix a proxy mounts it on.

This is a regression test for a live defect rather than a hypothetical: the LMU
deployment routes the service by `PathPrefix(/api/wallet/image-tools/v1)` and forwards
the prefix unchanged, the application mounted everything at its own root, and every
endpoint answered 404 -- which is how it was found, because `/docs` and the OpenAPI
document were unreachable at the address the service is published under.

The application object is built at import time, so each case re-imports the module
with the environment it is testing. `TestClient` is used WITHOUT its context manager
on purpose: entering it runs the lifespan, which loads the MediaPipe model, and none
of the routes exercised here needs a face analyzer.
"""

from edutap.image_api import settings as settings_module
from fastapi.testclient import TestClient

import importlib
import pytest


PREFIX = "/api/wallet/image-tools/v1"


def _reload_with_root_path(monkeypatch, root_path: str):
    """Return the application module as it is built under `root_path`."""
    # Tracing off: reloading the module re-runs `install_observability`, and a second
    # `logfire.configure()` in one process is noise this test has no use for.
    monkeypatch.setenv("EDUTAP_TELEMETRY_ENABLED", "false")
    monkeypatch.setenv("IMAGE_API_ROOT_PATH", root_path)
    # `get_settings` is `lru_cache`d, so the environment alone would not be read
    # again -- the application would be rebuilt from the previous case's settings.
    settings_module.get_settings.cache_clear()
    main = importlib.import_module("edutap.image_api.main")
    return importlib.reload(main)


@pytest.fixture(autouse=True)
def _restore_module_state():
    """Leave the imported module as the rest of the suite expects to find it."""
    yield
    settings_module.get_settings.cache_clear()
    importlib.reload(importlib.import_module("edutap.image_api.main"))


def test_unset_root_path_serves_the_bare_paths_only(monkeypatch):
    main = _reload_with_root_path(monkeypatch, "")
    client = TestClient(main.app)

    assert client.get("/").status_code == 200
    # The defect, stated as an expectation: without a root path the prefixed address
    # is simply not served.
    assert client.get(f"{PREFIX}/").status_code == 404
    assert client.get(f"{PREFIX}/openapi.json").status_code == 404


def test_root_path_serves_the_prefixed_paths(monkeypatch):
    main = _reload_with_root_path(monkeypatch, PREFIX)
    client = TestClient(main.app)

    assert main.app.root_path == PREFIX
    assert client.get(f"{PREFIX}/").status_code == 200
    assert client.get(f"{PREFIX}/docs").status_code == 200
    assert client.get(f"{PREFIX}/openapi.json").status_code == 200


def test_root_path_keeps_the_bare_paths_reachable(monkeypatch):
    """A container reached directly inside the overlay network must still work.

    Health checks and sibling services address the service by container name and
    without the proxy's prefix. Starlette keeps serving those, which is what makes
    setting a root path safe rather than a cutover.
    """
    main = _reload_with_root_path(monkeypatch, PREFIX)
    client = TestClient(main.app)

    assert client.get("/").status_code == 200


def test_openapi_document_names_the_deployed_address(monkeypatch):
    """A client generated from the document must call the address the service has.

    Without this the `servers` entry is absent, every generated client targets the
    bare root, and the mismatch surfaces as a 404 in someone else's codebase.
    """
    main = _reload_with_root_path(monkeypatch, PREFIX)
    client = TestClient(main.app)

    document = client.get(f"{PREFIX}/openapi.json").json()
    assert document["servers"] == [{"url": PREFIX}]
