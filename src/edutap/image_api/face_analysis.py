from dataclasses import dataclass

import math
import numpy as np


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
    """Decompose the rotation part of a 4x4 (or 3x3) matrix into Euler angles."""
    r = np.asarray(matrix, dtype=float)[:3, :3]
    sy = math.sqrt(r[0, 0] ** 2 + r[0, 2] ** 2)
    if sy > 1e-6:
        roll = math.atan2(r[1, 2], r[1, 1])
        pitch = math.atan2(-r[1, 0], sy)
        yaw = math.atan2(r[0, 2], r[0, 0])
    else:
        roll = math.atan2(r[2, 1], r[2, 2])
        pitch = math.atan2(-r[1, 0], sy)
        yaw = 0.0
    return HeadPose(
        yaw=math.degrees(yaw),
        pitch=math.degrees(pitch),
        roll=math.degrees(roll),
    )
