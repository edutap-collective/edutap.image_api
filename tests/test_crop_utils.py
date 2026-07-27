from PIL import Image
from edutap.image_api.crop_utils import crop_face_centered
from edutap.image_api.face_analysis import BBox


def test_crop_is_square_and_sized():
    image = Image.new("RGB", (1200, 800), "white")
    bbox = BBox(0.4, 0.35, 0.6, 0.65)
    out = crop_face_centered(image, bbox, size=256, margin_factor=1.6)
    assert out.size == (256, 256)


def test_crop_near_edge_stays_in_bounds():
    image = Image.new("RGB", (400, 400), "white")
    bbox = BBox(0.0, 0.0, 0.2, 0.2)
    out = crop_face_centered(image, bbox, size=128, margin_factor=2.0)
    assert out.size == (128, 128)
