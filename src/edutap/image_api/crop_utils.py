from PIL import Image

import cv2
import cv2.data


FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def crop_center(image: Image, width: int, height: int):
    img_width, img_height = image.size
    return image.crop(
        (
            (img_width - width) // 2,
            (img_height - height) // 2,
            (img_width + width) // 2,
            (img_height + height) // 2,
        )
    )


def crop_max_square_and_resize(image: Image):
    return crop_center(image, min(image.size), min(image.size))


def find_face(image_file) -> list[dict]:
    """
    Find Faces in Photo
    """
    result = []
    # Read
    cv_photo = cv2.imread(image_file)
    height, width, _ = cv_photo.shape

    # Convert into grayscale
    grayscale_photo = cv2.cvtColor(cv_photo, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = FACE_CASCADE.detectMultiScale(grayscale_photo, 1.1, 4)

    for x, y, w, h in faces:
        pass


    return result
