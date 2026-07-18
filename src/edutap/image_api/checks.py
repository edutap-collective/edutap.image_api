# src/edutap/image_api/checks.py
from .face_analysis import FaceAnalysisResult
from .settings import Settings
from .validation_models import CheckResult
from dataclasses import dataclass
from typing import Callable


@dataclass
class CheckContext:
    """Input for all checks: one analysis result plus the active settings."""

    result: FaceAnalysisResult
    settings: Settings


Check = Callable[[CheckContext], CheckResult]


def _single_face(ctx: CheckContext):
    faces = ctx.result.faces
    return faces[0] if len(faces) == 1 else None


def check_exactly_one_face(ctx: CheckContext) -> CheckResult:
    count = ctx.result.face_count
    return CheckResult(
        name="exactly_one_face",
        passed=count == 1,
        detail=f"{count} face(s) detected",
        measured={"face_count": count},
    )


def check_face_size(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="face_size", passed=False, detail="requires exactly one face"
        )
    ratio = face.bbox.area
    s = ctx.settings
    ok = s.min_face_area_ratio <= ratio <= s.max_face_area_ratio
    return CheckResult(
        name="face_size",
        passed=ok,
        detail=f"face area ratio {ratio:.3f}",
        measured={"area_ratio": round(ratio, 4)},
    )


def check_face_centered(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="face_centered", passed=False, detail="requires exactly one face"
        )
    cx, cy = face.bbox.center
    offset = max(abs(cx - 0.5), abs(cy - 0.5))
    ok = offset <= ctx.settings.max_center_offset_ratio
    return CheckResult(
        name="face_centered",
        passed=ok,
        detail=f"center offset {offset:.3f}",
        measured={"offset": round(offset, 4)},
    )


def check_frontal_pose(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="frontal_pose", passed=False, detail="requires exactly one face"
        )
    pose = face.head_pose
    s = ctx.settings
    ok = (
        abs(pose.yaw) <= s.max_yaw_deg
        and abs(pose.pitch) <= s.max_pitch_deg
        and abs(pose.roll) <= s.max_roll_deg
    )
    return CheckResult(
        name="frontal_pose",
        passed=ok,
        detail=f"yaw {pose.yaw:.1f}, pitch {pose.pitch:.1f}, roll {pose.roll:.1f}",
        measured={
            "yaw": round(pose.yaw, 1),
            "pitch": round(pose.pitch, 1),
            "roll": round(pose.roll, 1),
        },
    )


def check_eyes_open(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="eyes_open", passed=False, detail="requires exactly one face"
        )
    blink = max(
        face.blendshapes.get("eyeBlinkLeft", 0.0),
        face.blendshapes.get("eyeBlinkRight", 0.0),
    )
    ok = blink <= ctx.settings.eye_open_threshold
    return CheckResult(
        name="eyes_open",
        passed=ok,
        detail=f"max blink score {blink:.2f}",
        measured={"blink": round(blink, 3)},
    )


def check_no_sunglasses(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="no_sunglasses",
            passed=False,
            best_effort=True,
            detail="requires exactly one face",
        )
    eye_signal = any(
        v > 0.0
        for k, v in face.blendshapes.items()
        if k.startswith("eyeLook") or k.startswith("eyeBlink")
    )
    ok = face.has_iris and eye_signal
    return CheckResult(
        name="no_sunglasses",
        passed=ok,
        best_effort=True,
        detail="iris landmarks present"
        if ok
        else "eyes not clearly detected (sunglasses?)",
    )


def check_no_headwear(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="no_headwear",
            passed=False,
            best_effort=True,
            detail="requires exactly one face",
        )
    # Heuristic: if the face bbox reaches the very top edge, the forehead /
    # hairline is likely cropped or occluded by headwear.
    ok = face.bbox.y_min > 0.02
    return CheckResult(
        name="no_headwear",
        passed=ok,
        best_effort=True,
        detail="forehead region visible"
        if ok
        else "forehead region reaches image edge (headwear?)",
        measured={"forehead_top": round(face.bbox.y_min, 3)},
    )


ALL_CHECKS: list[Check] = [
    check_exactly_one_face,
    check_face_size,
    check_face_centered,
    check_frontal_pose,
    check_eyes_open,
    check_no_sunglasses,
    check_no_headwear,
]


def run_checks(ctx: CheckContext) -> list[CheckResult]:
    return [check(ctx) for check in ALL_CHECKS]


def overall_passed(results: list[CheckResult]) -> bool:
    return all(r.passed for r in results if not r.best_effort)


def warnings_from(results: list[CheckResult]) -> list[str]:
    return [f"{r.name}: {r.detail}" for r in results if r.best_effort and not r.passed]
