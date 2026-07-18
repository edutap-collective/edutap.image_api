# tests/test_endpoint_validate_and_crop.py
import base64
import io
import pathlib
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from edutap.image_api.main import app

TEST_IMAGES = pathlib.Path(__file__).parent / "test-images"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_rejects_non_image(client):
    resp = client.post(
        "/validate_and_crop/",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
        data={"size": "256"},
    )
    assert resp.status_code == 422


def test_size_out_of_bounds(client):
    resp = client.post(
        "/validate_and_crop/",
        files={"file": ("x.png", _png_bytes(), "image/png")},
        data={"size": "5"},
    )
    assert resp.status_code == 422


@pytest.mark.integration
def test_returns_report(client):
    with open(TEST_IMAGES / "1.jpg", "rb") as fh:
        resp = client.post(
            "/validate_and_crop/",
            files={"file": ("1.jpg", fh.read(), "image/jpeg")},
            data={"size": "256"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert "passed" in body
    assert isinstance(body["checks"], list)
    if body["output"]["image_base64"] is not None:
        raw = base64.b64decode(body["output"]["image_base64"])
        out = Image.open(io.BytesIO(raw))
        assert out.size == (256, 256)


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (300, 300), "white").save(buf, format="PNG")
    return buf.getvalue()
