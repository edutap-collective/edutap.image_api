# Biometric photo validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `POST /validate_and_crop/` endpoint that validates a portrait photo against pragmatic biometric criteria and returns a JSON report with a face-centered, scaled square crop embedded as Base64.

**Architecture:** A modular pipeline inside the existing FastAPI service. `face_analysis` wraps MediaPipe Face Landmarker into a neutral result object, `checks` maps that result to a list of check results, `crop_utils` produces the face-centered crop, and the endpoint orchestrates. All thresholds live in `pydantic-settings`.

**Tech Stack:** Python 3.10-3.12, FastAPI, Pydantic v2, pydantic-settings, MediaPipe Face Landmarker, Pillow, NumPy, pytest, anyio.

## Global Constraints

- Python floor: `requires-python = ">=3.10"`.
- MediaPipe (0.10.35) ships wheels only for Python 3.9-3.12, so the tox matrix caps at 3.12.
- Type hints on every public function; no bare `Any` without reason.
- async-first: no blocking calls on the async path; dispatch MediaPipe inference via `anyio.to_thread.run_sync`.
- Configuration only through `pydantic-settings`; no scattered `os.getenv`.
- TDD: write the failing test first, then the minimal implementation.
- Conventional Commits; never push (the user pushes); already on branch `feature/biometric-photo-validation`.
- License header context: EUPL 1.2 project.

---

## File structure

- `src/edutap/image_api/settings.py` — NEW: `Settings` (pydantic-settings), all thresholds and the model path.
- `src/edutap/image_api/validation_models.py` — NEW: Pydantic response models (`CheckResult`, `OutputImage`, `ValidationReport`).
- `src/edutap/image_api/face_analysis.py` — NEW: MediaPipe wrapper, geometry dataclasses, head-pose helper, `FaceAnalyzer`.
- `src/edutap/image_api/checks.py` — NEW: `CheckContext`, individual checks, `run_checks`.
- `src/edutap/image_api/crop_utils.py` — MODIFY: add `crop_face_centered`; remove the Haar cascade code.
- `src/edutap/image_api/main.py` — MODIFY: load the analyzer in `lifespan`, add the endpoint.
- `src/edutap/image_api/assets/face_landmarker.task` — NEW: bundled model file.
- `tests/test_settings.py`, `tests/test_validation_models.py`, `tests/test_face_analysis.py`, `tests/test_checks.py`, `tests/test_crop_utils.py`, `tests/test_endpoint_validate_and_crop.py` — NEW test modules.
- `pyproject.toml`, `MANIFEST.in`, `tox.ini` — MODIFY: dependencies, package data, Python matrix.

---

## Task 1: Dependencies, model asset, and Python matrix

**Files:**
- Modify: `pyproject.toml`
- Modify: `MANIFEST.in`
- Modify: `tox.ini`
- Create: `src/edutap/image_api/assets/face_landmarker.task`

**Interfaces:**
- Produces: an installed environment with `mediapipe`, `numpy`, `anyio`, `httpx`, `pytest-asyncio`; the model file at `src/edutap/image_api/assets/face_landmarker.task`.

- [ ] **Step 1: Edit `pyproject.toml` dependencies**

In `[project].dependencies` remove `"opencv-python"` and add `"mediapipe>=0.10.14"`, `"numpy"`, `"anyio"`.
In `[project.optional-dependencies].test` add `"httpx"` and `"pytest-asyncio"`.

```toml
dependencies = [
    "pydantic[email,dotenv]>=2.0",
    "pydantic-settings>=2.0",
    "python-dotenv",
    "fastapi",
    "fastapi-chameleon",
    "python-multipart",
    "uvicorn",
    "requests",
    "aiokafka",
    "pillow",
    "numpy",
    "anyio",
    "mediapipe>=0.10.14",
]
```

```toml
test = [
    "pytest",
    "pytest-asyncio",
    "httpx",
    "requests-mock",
]
```

- [ ] **Step 2: Add package data for the model**

Append to `pyproject.toml`:

```toml
[tool.setuptools.package-data]
"edutap.image_api" = ["assets/*.task"]
```

Add to `MANIFEST.in`:

```text
recursive-include src/edutap/image_api/assets *.task
```

- [ ] **Step 3: Cap the tox Python matrix at 3.12**

In `tox.ini`, ensure the `envlist` covers only `py310, py311, py312` (remove any `py313`). Add a one-line comment: `# mediapipe ships wheels only up to Python 3.12`.

- [ ] **Step 4: Download the model file**

Run:

```console
curl -L -o src/edutap/image_api/assets/face_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

Expected: a file of roughly 3-4 MB at that path.

- [ ] **Step 5: Install and verify import**

Run:

```console
uv pip install -U -e ".[test,typecheck,develop]"
python -c "import mediapipe, numpy; print('ok')"
```

Expected: prints `ok`.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml MANIFEST.in tox.ini src/edutap/image_api/assets/face_landmarker.task
git commit -m "build: add mediapipe and numpy, bundle face landmarker model, cap tox at py312"
```

---

## Task 2: Settings

**Files:**
- Create: `src/edutap/image_api/settings.py`
- Test: `tests/test_settings.py`

**Interfaces:**
- Produces:
  ```python
  class Settings(BaseSettings):
      min_face_area_ratio: float
      max_face_area_ratio: float
      max_center_offset_ratio: float
      max_yaw_deg: float
      max_pitch_deg: float
      max_roll_deg: float
      eye_open_threshold: float
      crop_margin_factor: float
      default_output_size: int
      min_output_size: int
      max_output_size: int
      model_path: str
  def get_settings() -> Settings  # cached
  ```

- [ ] **Step 1: Write the failing test**

```python
# tests/test_settings.py
from edutap.image_api.settings import Settings, get_settings


def test_defaults_are_sane():
    s = Settings()
    assert 0 < s.min_face_area_ratio < s.max_face_area_ratio <= 1.0
    assert s.default_output_size == 512
    assert s.min_output_size <= s.default_output_size <= s.max_output_size
    assert s.model_path.endswith("face_landmarker.task")


def test_env_override(monkeypatch):
    monkeypatch.setenv("IMAGE_API_MAX_YAW_DEG", "25")
    assert Settings().max_yaw_deg == 25.0


def test_get_settings_is_cached():
    assert get_settings() is get_settings()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings.py -v`
Expected: FAIL with `ModuleNotFoundError: edutap.image_api.settings`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/edutap/image_api/settings.py
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

import pathlib


BASE_DIR = pathlib.Path(__file__).parent.resolve()
DEFAULT_MODEL_PATH = str(BASE_DIR / "assets" / "face_landmarker.task")


class Settings(BaseSettings):
    """Runtime configuration for image validation and cropping."""

    model_config = SettingsConfigDict(env_prefix="IMAGE_API_", env_file=".env")

    min_face_area_ratio: float = 0.05
    max_face_area_ratio: float = 0.80
    max_center_offset_ratio: float = 0.15
    max_yaw_deg: float = 15.0
    max_pitch_deg: float = 15.0
    max_roll_deg: float = 10.0
    eye_open_threshold: float = 0.5
    crop_margin_factor: float = 1.6
    default_output_size: int = 512
    min_output_size: int = 16
    max_output_size: int = 4096
    model_path: str = DEFAULT_MODEL_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Note: the field `model_path` starts with `model_`, which Pydantic protects by default. `env_prefix` plus the explicit field is fine, but if Pydantic warns about the `model_` namespace, add `protected_namespaces=()` to `model_config`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/edutap/image_api/settings.py tests/test_settings.py
git commit -m "feat: add pydantic-settings configuration for validation thresholds"
```

---

## Task 3: Response models

**Files:**
- Create: `src/edutap/image_api/validation_models.py`
- Test: `tests/test_validation_models.py`

**Interfaces:**
- Produces:
  ```python
  class CheckResult(BaseModel):
      name: str
      passed: bool
      best_effort: bool = False
      detail: str = ""
      measured: dict[str, float | int] = {}
  class OutputImage(BaseModel):
      width: int
      height: int
      format: str = "png"
      image_base64: str | None = None
  class ValidationReport(BaseModel):
      passed: bool
      crop_mode: Literal["face"] | None = None
      checks: list[CheckResult]
      warnings: list[str] = []
      output: OutputImage
  ```

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validation_models.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation_models.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/edutap/image_api/validation_models.py
from pydantic import BaseModel
from pydantic import Field
from typing import Literal


class CheckResult(BaseModel):
    """Result of a single validation check."""

    name: str
    passed: bool
    best_effort: bool = False
    detail: str = ""
    measured: dict[str, float | int] = Field(default_factory=dict)


class OutputImage(BaseModel):
    """Metadata and payload of the processed image."""

    width: int
    height: int
    format: str = "png"
    image_base64: str | None = None


class ValidationReport(BaseModel):
    """Full report returned by the validate_and_crop endpoint."""

    passed: bool
    crop_mode: Literal["face"] | None = None
    checks: list[CheckResult]
    warnings: list[str] = Field(default_factory=list)
    output: OutputImage
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation_models.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/edutap/image_api/validation_models.py tests/test_validation_models.py
git commit -m "feat: add pydantic response models for validation report"
```

---

## Task 4: Face-analysis geometry helpers

**Files:**
- Create: `src/edutap/image_api/face_analysis.py`
- Test: `tests/test_face_analysis.py`

**Interfaces:**
- Produces:
  ```python
  @dataclass(frozen=True)
  class BBox:
      x_min: float; y_min: float; x_max: float; y_max: float
      @property
      def width(self) -> float
      @property
      def height(self) -> float
      @property
      def center(self) -> tuple[float, float]
      @property
      def area(self) -> float
  @dataclass(frozen=True)
  class HeadPose:
      yaw: float; pitch: float; roll: float
  def bbox_from_landmarks(points: list[tuple[float, float]]) -> BBox
  def head_pose_from_matrix(matrix: "np.ndarray") -> HeadPose
  ```
  Landmark coordinates are normalized to `[0, 1]`. Angles are in degrees.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_face_analysis.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_face_analysis.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/edutap/image_api/face_analysis.py
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
    sy = math.sqrt(r[0, 0] ** 2 + r[1, 0] ** 2)
    if sy > 1e-6:
        roll = math.atan2(r[2, 1], r[2, 2])
        pitch = math.atan2(-r[2, 0], sy)
        yaw = math.atan2(r[1, 0], r[0, 0])
    else:
        roll = math.atan2(-r[1, 2], r[1, 1])
        pitch = math.atan2(-r[2, 0], sy)
        yaw = 0.0
    return HeadPose(
        yaw=math.degrees(yaw),
        pitch=math.degrees(pitch),
        roll=math.degrees(roll),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_face_analysis.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add src/edutap/image_api/face_analysis.py tests/test_face_analysis.py
git commit -m "feat: add face geometry helpers (bbox and head pose)"
```

---

## Task 5: FaceAnalyzer and result types

**Files:**
- Modify: `src/edutap/image_api/face_analysis.py`
- Test: `tests/test_face_analysis.py` (add integration tests)

**Interfaces:**
- Consumes: `BBox`, `HeadPose`, `bbox_from_landmarks`, `head_pose_from_matrix` from Task 4.
- Produces:
  ```python
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
      faces: list[Face]
      @property
      def face_count(self) -> int
  class FaceAnalyzer:
      def __init__(self, model_path: str, num_faces: int = 5) -> None  # raises FileNotFoundError
      def analyze(self, image: "PIL.Image.Image") -> FaceAnalysisResult
      def close(self) -> None
  ```
  `blendshapes` maps MediaPipe category names (for example `eyeBlinkLeft`) to scores in `[0, 1]`.

- [ ] **Step 1: Write the failing integration test**

```python
# append to tests/test_face_analysis.py
import pathlib
import pytest
from PIL import Image
from edutap.image_api.face_analysis import FaceAnalyzer
from edutap.image_api.settings import get_settings

TEST_IMAGES = pathlib.Path(__file__).parent / "test-images"


@pytest.fixture(scope="module")
def analyzer():
    a = FaceAnalyzer(get_settings().model_path)
    yield a
    a.close()


def test_missing_model_raises():
    with pytest.raises(FileNotFoundError):
        FaceAnalyzer("/nonexistent/model.task")


@pytest.mark.integration
def test_analyze_returns_faces(analyzer):
    image = Image.open(TEST_IMAGES / "1.jpg").convert("RGB")
    result = analyzer.analyze(image)
    assert result.image_width == image.width
    assert result.image_height == image.height
    assert result.face_count >= 0
    for face in result.faces:
        assert 0.0 <= face.bbox.x_min <= 1.0
        assert isinstance(face.blendshapes, dict)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_face_analysis.py::test_missing_model_raises -v`
Expected: FAIL with `ImportError` / `AttributeError` (no `FaceAnalyzer`).

- [ ] **Step 3: Register the `integration` marker**

Add to `pyproject.toml` under `[tool.pytest.ini_options]`:

```toml
markers = [
    "integration: tests that load the MediaPipe model and real images",
]
asyncio_mode = "auto"
```

- [ ] **Step 4: Write minimal implementation**

Append to `src/edutap/image_api/face_analysis.py`:

```python
from dataclasses import dataclass
from PIL import Image

import pathlib
import threading

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision


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


# MediaPipe iris landmark indices (refine_landmarks adds indices 468-477).
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
            faces.append(Face(bbox=bbox, head_pose=pose, blendshapes=shapes, has_iris=has_iris))

        return FaceAnalysisResult(
            image_width=rgb.width,
            image_height=rgb.height,
            faces=faces,
        )

    def close(self) -> None:
        self._landmarker.close()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_face_analysis.py -v`
Expected: PASS. The `test_analyze_returns_faces` test runs the real model.

- [ ] **Step 6: Commit**

```bash
git add src/edutap/image_api/face_analysis.py tests/test_face_analysis.py pyproject.toml
git commit -m "feat: add MediaPipe FaceAnalyzer producing neutral analysis result"
```

---

## Task 6: Check pipeline

**Files:**
- Create: `src/edutap/image_api/checks.py`
- Test: `tests/test_checks.py`

**Interfaces:**
- Consumes: `FaceAnalysisResult`, `Face`, `BBox`, `HeadPose` from Tasks 4-5; `Settings` from Task 2; `CheckResult` from Task 3.
- Produces:
  ```python
  @dataclass
  class CheckContext:
      result: FaceAnalysisResult
      settings: Settings
  Check = Callable[[CheckContext], CheckResult]
  ALL_CHECKS: list[Check]
  def run_checks(ctx: CheckContext) -> list[CheckResult]
  def overall_passed(results: list[CheckResult]) -> bool
  def warnings_from(results: list[CheckResult]) -> list[str]
  ```

- [ ] **Step 1: Write the failing tests**

```python
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


def _face(bbox=BBox(0.35, 0.30, 0.65, 0.75), yaw=0.0, pitch=0.0, roll=0.0,
          blink=0.1, has_iris=True):
    return Face(
        bbox=bbox,
        head_pose=HeadPose(yaw=yaw, pitch=pitch, roll=roll),
        blendshapes={"eyeBlinkLeft": blink, "eyeBlinkRight": blink,
                     "eyeLookInLeft": 0.2},
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_checks.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

Create `src/edutap/image_api/checks.py` with exactly this content:

```python
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
        return CheckResult(name="face_size", passed=False, detail="requires exactly one face")
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
        return CheckResult(name="face_centered", passed=False, detail="requires exactly one face")
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
        return CheckResult(name="frontal_pose", passed=False, detail="requires exactly one face")
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
        return CheckResult(name="eyes_open", passed=False, detail="requires exactly one face")
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
            name="no_sunglasses", passed=False, best_effort=True,
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
        detail="iris landmarks present" if ok else "eyes not clearly detected (sunglasses?)",
    )


def check_no_headwear(ctx: CheckContext) -> CheckResult:
    face = _single_face(ctx)
    if face is None:
        return CheckResult(
            name="no_headwear", passed=False, best_effort=True,
            detail="requires exactly one face",
        )
    # Heuristic: if the face bbox reaches the very top edge, the forehead /
    # hairline is likely cropped or occluded by headwear.
    ok = face.bbox.y_min > 0.02
    return CheckResult(
        name="no_headwear",
        passed=ok,
        best_effort=True,
        detail="forehead region visible" if ok else "forehead region reaches image edge (headwear?)",
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_checks.py -v`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add src/edutap/image_api/checks.py tests/test_checks.py
git commit -m "feat: add biometric check pipeline with hard and best-effort checks"
```

---

## Task 7: Face-centered crop

**Files:**
- Modify: `src/edutap/image_api/crop_utils.py`
- Test: `tests/test_crop_utils.py`

**Interfaces:**
- Consumes: `BBox` from Task 4.
- Produces:
  ```python
  def crop_face_centered(image: Image.Image, bbox: BBox, size: int, margin_factor: float) -> Image.Image
  ```
  Returns a `size` by `size` RGB image centered on the bbox center.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_crop_utils.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_crop_utils.py -v`
Expected: FAIL with `ImportError` (no `crop_face_centered`).

- [ ] **Step 3: Rewrite `crop_utils.py`**

Replace the whole file with (this removes the Haar cascade and its `cv2` import):

```python
# src/edutap/image_api/crop_utils.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_crop_utils.py -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add src/edutap/image_api/crop_utils.py tests/test_crop_utils.py
git commit -m "feat: add face-centered square crop, remove opencv haar cascade"
```

---

## Task 8: Endpoint and lifespan wiring

**Files:**
- Modify: `src/edutap/image_api/main.py`
- Test: `tests/test_endpoint_validate_and_crop.py`

**Interfaces:**
- Consumes: `FaceAnalyzer` (Task 5), `CheckContext`/`run_checks`/`overall_passed`/`warnings_from` (Task 6), `crop_face_centered` (Task 7), `ValidationReport`/`OutputImage` (Task 3), `get_settings` (Task 2).
- Produces: `POST /validate_and_crop/` returning `ValidationReport`.

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_endpoint_validate_and_crop.py -v`
Expected: FAIL (endpoint returns 404).

- [ ] **Step 3: Add imports and lifespan wiring to `main.py`**

Add near the existing imports:

```python
from .checks import CheckContext
from .checks import overall_passed
from .checks import run_checks
from .checks import warnings_from
from .crop_utils import crop_face_centered
from .face_analysis import FaceAnalyzer
from .settings import get_settings
from .validation_models import OutputImage
from .validation_models import ValidationReport
from fastapi import HTTPException
from PIL import UnidentifiedImageError

import anyio
import base64
import io
```

Replace the `lifespan` body so it loads and releases the analyzer:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start eduTAP Image API Service")
    settings = get_settings()
    app.state.face_analyzer = FaceAnalyzer(settings.model_path)
    yield
    app.state.face_analyzer.close()
    logger.info("Shutdown eduTAP Image API Service")
```

- [ ] **Step 4: Add the endpoint to `main.py`**

```python
@app.post("/validate_and_crop/")
async def validate_and_crop(
    file: Annotated[UploadFile, File(description="Portrait image")],
    size: Annotated[int, Form(description="Output edge length in px", ge=16, le=4096)] = 512,
) -> ValidationReport:
    try:
        image = Image.open(file.file)
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=422, detail=f"Unreadable image: {exc}")

    analyzer: FaceAnalyzer = app.state.face_analyzer
    result = await anyio.to_thread.run_sync(analyzer.analyze, image)

    ctx = CheckContext(result=result, settings=get_settings())
    checks = run_checks(ctx)

    crop_mode = None
    output = OutputImage(width=size, height=size, image_base64=None)
    if result.face_count == 1:
        cropped = crop_face_centered(
            image, result.faces[0].bbox, size, get_settings().crop_margin_factor
        )
        buffer = io.BytesIO()
        cropped.save(buffer, format="PNG", optimize=True)
        output.image_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        crop_mode = "face"

    return ValidationReport(
        passed=overall_passed(checks),
        crop_mode=crop_mode,
        checks=checks,
        warnings=warnings_from(checks),
        output=output,
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_endpoint_validate_and_crop.py -v`
Expected: PASS (3 tests; the integration test loads the model).

- [ ] **Step 6: Run the whole suite and linters**

Run:

```console
pytest -q
uv run ruff check src tests
uv run ruff format src tests
```

Expected: all tests pass, ruff clean.

- [ ] **Step 7: Commit**

```bash
git add src/edutap/image_api/main.py tests/test_endpoint_validate_and_crop.py
git commit -m "feat: add POST /validate_and_crop/ endpoint with report and cropped image"
```

---

## Task 9: Documentation

**Files:**
- Create: `docs/how-to/validate-a-portrait-photo.md`
- Create: `docs/reference/validate-and-crop.md`
- Modify: `docs/how-to/index.md`, `docs/reference/index.md`, `docs/index.md`

**Interfaces:**
- Consumes: the final endpoint contract from Task 8.

- [ ] **Step 1: Write the reference page**

Create `docs/reference/validate-and-crop.md` documenting the endpoint: method, path, form parameters (`file`, `size` with bounds and default 512), every check name with its type (hard or best-effort), the `ValidationReport` JSON schema, and the status codes (200 always on a readable image, 422 on unreadable image or out-of-bounds `size`). Follow the Reference quadrant: factual, table-driven, no instruction. Note that `passed` reflects hard checks only and best-effort failures appear in `warnings`.

- [ ] **Step 2: Write the how-to page**

Create `docs/how-to/validate-a-portrait-photo.md` following the How-to quadrant: a `curl` example that posts an image with `size`, how to read `passed`, `checks`, and `warnings`, and how to decode `output.image_base64` to a PNG file. Link to the reference page for the full parameter list.

- [ ] **Step 3: Add both pages to the toctrees**

Add `validate-a-portrait-photo` to the toctree in `docs/how-to/index.md` and to the how-to list in `docs/index.md`.
Add `validate-and-crop` to the toctree in `docs/reference/index.md` and to the reference list in `docs/index.md`.

- [ ] **Step 4: Commit**

```bash
git add docs/
git commit -m "docs: document the validate_and_crop endpoint (reference and how-to)"
```

---

## Self-review notes

- Spec coverage: endpoint (Task 8), always-JSON report with Base64 (Task 8 + Task 3), pragmatic core checks (Task 6), best-effort accessory heuristics (Task 6), MediaPipe replaces cascade (Tasks 5 and 7), face-centered crop with size param (Tasks 7 and 8), settings (Task 2), fail-fast model load (Task 8 lifespan + Task 5 `FileNotFoundError`), 422 handling (Task 8), threadpool inference and lock (Tasks 5 and 8), dependency and Python-matrix caveat (Task 1), docs follow-up (Task 9).
- `passed` semantics (`overall_passed` ignores best-effort) match the spec.
- Type names are consistent across tasks: `BBox`, `HeadPose`, `Face`, `FaceAnalysisResult`, `FaceAnalyzer`, `CheckContext`, `CheckResult`, `OutputImage`, `ValidationReport`.
