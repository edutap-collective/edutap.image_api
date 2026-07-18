import math
import numpy as np
from edutap.image_api.face_analysis import BBox
from edutap.image_api.face_analysis import bbox_from_landmarks
from edutap.image_api.face_analysis import head_pose_from_matrix


def test_bbox_from_landmarks():
    box = bbox_from_landmarks([(0.2, 0.3), (0.6, 0.9), (0.4, 0.1)])
    assert box.x_min == 0.2 and box.x_max == 0.6
    assert box.y_min == 0.1 and box.y_max == 0.9
    assert math.isclose(box.width, 0.4)
    assert math.isclose(box.height, 0.8)
    assert box.center == (0.4, 0.5)
    assert math.isclose(box.area, 0.32)


def test_head_pose_identity_is_zero():
    pose = head_pose_from_matrix(np.eye(4))
    assert abs(pose.yaw) < 1e-6
    assert abs(pose.pitch) < 1e-6
    assert abs(pose.roll) < 1e-6


def test_head_pose_yaw_rotation():
    angle = math.radians(30)
    rot = np.eye(4)
    rot[0, 0] = math.cos(angle)
    rot[0, 2] = math.sin(angle)
    rot[2, 0] = -math.sin(angle)
    rot[2, 2] = math.cos(angle)
    pose = head_pose_from_matrix(rot)
    assert abs(abs(pose.yaw) - 30) < 1.0
