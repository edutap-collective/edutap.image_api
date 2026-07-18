from .face_analysis import BBox
from PIL import Image


def crop_center(image: Image.Image, width: int, height: int) -> Image.Image:
    img_width, img_height = image.size
    return image.crop(
        (
            (img_width - width) // 2,
            (img_height - height) // 2,
            (img_width + width) // 2,
            (img_height + height) // 2,
        )
    )


def crop_max_square_and_resize(image: Image.Image) -> Image.Image:
    return crop_center(image, min(image.size), min(image.size))


def crop_face_centered(
    image: Image.Image,
    bbox: BBox,
    size: int,
    margin_factor: float,
) -> Image.Image:
    """Crop a square centered on the face bbox, then resize to size by size."""
    img = image.convert("RGB")
    w, h = img.size
    cx = bbox.center[0] * w
    cy = bbox.center[1] * h

    side = bbox.height * h * margin_factor
    side = min(side, w, h)
    half = side / 2

    left = cx - half
    top = cy - half
    # Shift the square fully inside the image instead of shrinking it.
    left = max(0.0, min(left, w - side))
    top = max(0.0, min(top, h - side))

    box = (round(left), round(top), round(left + side), round(top + side))
    square = img.crop(box)
    return square.resize((size, size))
