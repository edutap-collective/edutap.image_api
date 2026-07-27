# tests/test_checks.py
from edutap.image_api.checks import CheckContext
from edutap.image_api.checks import overall_passed
from edutap.image_api.checks import run_checks
from edutap.image_api.checks import warnings_from
from edutap.image_api.face_analysis import BBox
from edutap.image_api.face_analysis import Face
from edutap.image_api.face_analysis import FaceAnalysisResult
from edutap.image_api.face_analysis import HeadPose
from edutap.image_api.settings import Settings


def _face(
    bbox=BBox(0.35, 0.30, 0.65, 0.75),
    yaw=0.0,
    pitch=0.0,
    roll=0.0,
    blink=0.1,
    has_iris=True,
):
    return Face(
        bbox=bbox,
        head_pose=HeadPose(yaw=yaw, pitch=pitch, roll=roll),
        blendshapes={
            "eyeBlinkLeft": blink,
            "eyeBlinkRight": blink,
            "eyeLookInLeft": 0.2,
        },
        has_iris=has_iris,
    )


def _ctx(faces):
    return CheckContext(
        result=FaceAnalysisResult(image_width=1000, image_height=1000, faces=faces),
        settings=Settings(),
    )


def _by_name(results):
    return {r.name: r for r in results}


def test_good_photo_passes_all_hard_checks():
    results = run_checks(_ctx([_face()]))
    assert overall_passed(results) is True


def test_two_faces_fails_single_face_check():
    results = _by_name(run_checks(_ctx([_face(), _face()])))
    assert results["exactly_one_face"].passed is False
    assert overall_passed(list(results.values())) is False


def test_zero_faces_fails():
    results = run_checks(_ctx([]))
    assert overall_passed(results) is False


def test_off_center_face_fails_centered_check():
    results = _by_name(run_checks(_ctx([_face(bbox=BBox(0.0, 0.0, 0.3, 0.3))])))
    assert results["face_centered"].passed is False


def test_rotated_face_fails_frontal_check():
    results = _by_name(run_checks(_ctx([_face(yaw=40.0)])))
    assert results["frontal_pose"].passed is False


def test_closed_eyes_fail_eyes_open_check():
    results = _by_name(run_checks(_ctx([_face(blink=0.9)])))
    assert results["eyes_open"].passed is False


def test_no_iris_warns_sunglasses_but_does_not_fail_overall():
    results = run_checks(_ctx([_face(has_iris=False)]))
    named = _by_name(results)
    assert named["no_sunglasses"].best_effort is True
    assert named["no_sunglasses"].passed is False
    assert overall_passed(results) is True
    assert any("no_sunglasses" in w for w in warnings_from(results))
