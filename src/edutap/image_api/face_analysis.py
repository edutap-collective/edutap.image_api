from dataclasses import dataclass
from PIL import Image

import math
import numpy as np
import pathlib
import threading

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision


@dataclass(frozen=True)
class BBox:
    """Axis-aligned bounding box in normalized [0, 1] coordinates."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class HeadPose:
    """Head orientation in degrees."""

    yaw: float
    pitch: float
    roll: float


def bbox_from_landmarks(points: list[tuple[float, float]]) -> BBox:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return BBox(min(xs), min(ys), max(xs), max(ys))


def head_pose_from_matrix(matrix: np.ndarray) -> HeadPose:
    """Decompose the rotation part of a 4x4 (or 3x3) matrix into Euler angles.

    Follows MediaPipe's canonical face coordinate system (+X to the subject's
    left, +Y up, +Z out of the face toward the camera): a rotation about X is
    a head nod and is reported as ``pitch``, a rotation about Y is a head turn
    and is reported as ``yaw``, and a rotation about Z is a head tilt and is
    reported as ``roll``.
    """
    r = np.asarray(matrix, dtype=float)[:3, :3]
    sy = math.sqrt(r[0, 0] ** 2 + r[0, 2] ** 2)
    if sy > 1e-6:
        pitch = math.atan2(r[1, 2], r[1, 1])
        roll = math.atan2(-r[1, 0], sy)
        yaw = math.atan2(r[0, 2], r[0, 0])
    else:
        pitch = math.atan2(r[2, 1], r[2, 2])
        roll = math.atan2(-r[1, 0], sy)
        yaw = 0.0
    return HeadPose(
        yaw=math.degrees(yaw),
        pitch=math.degrees(pitch),
        roll=math.degrees(roll),
    )


@dataclass(frozen=True)
class Face:
    bbox: BBox
    head_pose: HeadPose
    blendshapes: dict[str, float]
    has_iris: bool


@dataclass(frozen=True)
class FaceAnalysisResult:
    image_width: int
    image_height: int
    faces: list["Face"]

    @property
    def face_count(self) -> int:
        return len(self.faces)


# The bundled face_landmarker model returns 478 landmarks by default, with
# iris landmarks at indices 468-477.
_IRIS_INDEX_MIN = 468


class FaceAnalyzer:
    """Thread-safe wrapper around MediaPipe Face Landmarker."""

    def __init__(self, model_path: str, num_faces: int = 5) -> None:
        if not pathlib.Path(model_path).is_file():
            raise FileNotFoundError(f"Face landmarker model not found: {model_path}")
        options = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=mp_vision.RunningMode.IMAGE,
            num_faces=num_faces,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
        )
        self._landmarker = mp_vision.FaceLandmarker.create_from_options(options)
        self._lock = threading.Lock()

    def analyze(self, image: Image.Image) -> FaceAnalysisResult:
        rgb = image.convert("RGB")
        np_image = np.asarray(rgb)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_image)
        with self._lock:
            result = self._landmarker.detect(mp_image)

        faces: list[Face] = []
        matrixes = result.facial_transformation_matrixes or []
        blendshape_lists = result.face_blendshapes or []
        for idx, landmarks in enumerate(result.face_landmarks):
            points = [(lm.x, lm.y) for lm in landmarks]
            bbox = bbox_from_landmarks(points)
            matrix = np.asarray(matrixes[idx]) if idx < len(matrixes) else np.eye(4)
            pose = head_pose_from_matrix(matrix)
            shapes: dict[str, float] = {}
            if idx < len(blendshape_lists):
                shapes = {c.category_name: c.score for c in blendshape_lists[idx]}
            has_iris = len(landmarks) > _IRIS_INDEX_MIN
            faces.append(
                Face(bbox=bbox, head_pose=pose, blendshapes=shapes, has_iris=has_iris)
            )

        return FaceAnalysisResult(
            image_width=rgb.width,
            image_height=rgb.height,
            faces=faces,
        )

    def close(self) -> None:
        self._landmarker.close()
