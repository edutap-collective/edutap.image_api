from edutap.image_api.validation_models import CheckResult
from edutap.image_api.validation_models import OutputImage
from edutap.image_api.validation_models import ValidationReport


def test_check_result_defaults():
    r = CheckResult(name="exactly_one_face", passed=True)
    assert r.best_effort is False
    assert r.detail == ""
    assert r.measured == {}


def test_report_round_trip():
    report = ValidationReport(
        passed=False,
        crop_mode="face",
        checks=[CheckResult(name="frontal_pose", passed=False, detail="yaw too high")],
        warnings=["no_headwear: best-effort"],
        output=OutputImage(width=512, height=512, image_base64=None),
    )
    data = report.model_dump()
    assert data["passed"] is False
    assert data["output"]["image_base64"] is None
    assert data["checks"][0]["name"] == "frontal_pose"
