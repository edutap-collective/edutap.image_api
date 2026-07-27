# Design: biometric photo validation and face-centered crop

Date: 2026-07-17
Status: approved (design), pending implementation plan
Branch: `feature/biometric-photo-validation`

## Overview

The eduTAP Image API Service gains a new endpoint that accepts a photo of a person, validates it against a pragmatic set of biometric criteria, crops it to a face-centered square, scales it to a target size, and returns a JSON report with the processed image embedded as Base64.

The feature answers four questions about an uploaded photo:

1. Is there exactly one person in the image?
2. Is the face reasonably aligned (large enough, centered, roughly frontal, eyes open)?
3. Are there no obvious foreign objects such as sunglasses or headwear? (best-effort heuristic)
4. Produce a face-centered square crop, scaled to a requested size.

Face detection and geometry come from Google MediaPipe Face Landmarker, which replaces the existing OpenCV Haar cascade in `crop_utils.py`.

## Goals

- One new endpoint `POST /validate_and_crop/`.
- Always return a structured JSON report, even when validation fails.
- Embed the processed image as Base64 when a single face is available; otherwise `image_base64` is `null`.
- Keep every check independently testable and extensible.
- Centralize all thresholds in `pydantic-settings`.

## Non-goals

- Strict ICAO 9303 / ISO-IEC 19794-5 conformance. The checks are a pragmatic core; ICAO refinements can be added later as additional checks.
- A dedicated machine-learning classifier for accessories (sunglasses, hats). Foreign-object detection is a best-effort landmark heuristic in this iteration; a classifier check can dock onto the same interface later.
- A separate deployable microservice. This iteration adds the feature to the existing single FastAPI service.

## Decisions (from brainstorming)

- Response contract: always a JSON report with the image embedded as Base64.
- Biometric strictness: pragmatic core, built as an extensible check pipeline.
- Foreign objects: lightweight landmark heuristic, marked `best_effort`.
- Detection backend: MediaPipe Face Landmarker replaces the Haar cascade.
- Crop: face-centered square, target edge length as a parameter (default 512 px).
- Architecture: modular check pipeline inside the existing service (approach A).
- `passed` is decided by the hard checks only; best-effort failures become `warnings`.

## Architecture

New and changed modules under `src/edutap/image_api/`:

```
settings.py           # NEW: pydantic-settings, thresholds + model path
face_analysis.py      # NEW: MediaPipe wrapper (replaces Haar cascade)
checks.py             # NEW: Check protocol + concrete checks + runner
validation_models.py  # NEW: Pydantic response models
crop_utils.py         # CHANGED: add crop_face_centered(); remove cascade
models.py             # unchanged (wallet definitions stay)
main.py               # CHANGED: add POST /validate_and_crop/
assets/face_landmarker.task  # NEW: bundled model (~3-4 MB), path overridable
```

Each unit has a single purpose and a narrow interface:

- `face_analysis` maps MediaPipe output to a neutral context object.
- `checks` maps a context to a list of results and knows nothing about MediaPipe or HTTP.
- `crop_utils` maps image plus geometry to an image.
- `main` orchestrates and owns the HTTP contract.

### `face_analysis.py`

Wraps MediaPipe Face Landmarker (Tasks API) with `refine_landmarks=True` so iris landmarks are available.

- The landmarker is created once during the FastAPI `lifespan` and stored on the app.
- Inference is blocking and CPU-bound, so the endpoint calls it via `anyio.to_thread.run_sync`.
- The landmarker is not thread-safe, so `analyze` is guarded by a `threading.Lock`.
- `num_faces` is set high enough (for example 5) so that "more than one person" is detectable.

`analyze(image) -> FaceAnalysisResult` returns:

- `face_count: int`
- per face: `bbox` (from landmark extrema), `head_pose` (yaw, pitch, roll from `facial_transformation_matrix`), `blendshapes: dict[str, float]`, `landmarks`.

Head pose is derived by decomposing the rotation part of the 4x4 transformation matrix into Euler angles.

### `checks.py`

A `Check` protocol with `name` and `run(ctx) -> CheckResult`, plus a runner `run_checks(ctx) -> list[CheckResult]`.
The context carries the `FaceAnalysisResult`, the image dimensions, and the settings.

Concrete checks:

| Check | Criterion | Type |
|-------|-----------|------|
| `exactly_one_face` | `face_count == 1` | hard |
| `face_size` | face area / image area within `[min, max]` | hard |
| `face_centered` | offset of face center from image center below tolerance | hard |
| `frontal_pose` | absolute yaw, pitch, roll below tolerances | hard |
| `eyes_open` | eye-blink blendshapes below threshold | hard |
| `no_sunglasses` | iris landmarks present and eye blendshapes plausible | best_effort |
| `no_headwear` | forehead / upper-head region unobstructed and plausible | best_effort |

`passed` overall is true when every hard check passes.
Best-effort failures are collected into `warnings` rather than failing the report, because the heuristic is intentionally weak.

### `crop_utils.py`

- Add `crop_face_centered(image, face_geometry, size, margin_factor) -> Image`.
  The crop is a square centered on the face center, with a side length of face height times `margin_factor`, clamped to the image bounds, then resized to `size` by `size`.
- Keep `crop_center` and `crop_max_square_and_resize`.
- Remove `find_face`, `FACE_CASCADE`, and the OpenCV import.

### `validation_models.py`

Pydantic v2 models for the response:

- `CheckResult`: `name`, `passed`, `best_effort`, `detail`, `measured: dict`.
- `OutputImage`: `width`, `height`, `format`, `image_base64: str | None`.
- `ValidationReport`: `passed`, `crop_mode: Literal["face"] | None`, `checks: list[CheckResult]`, `warnings: list[str]`, `output: OutputImage`.

### `settings.py`

`pydantic-settings` `Settings`, overridable via environment, with defaults:

- `min_face_area_ratio` (0.05), `max_face_area_ratio` (0.8)
- `max_center_offset_ratio` (0.15)
- `max_yaw_deg` (15), `max_pitch_deg` (15), `max_roll_deg` (10)
- `eye_open_threshold` (blink blendshape maximum, 0.5)
- `crop_margin_factor` (1.6)
- `default_output_size` (512), plus bounds `min_output_size` (16), `max_output_size` (4096)
- `model_path` (default: the bundled `assets/face_landmarker.task`)

## Data flow

`POST /validate_and_crop/` with form parameters `file` (image) and `size: int = 512` (bounded 16-4096).

1. PIL opens the image; an unreadable image raises `422`.
2. `analyze` runs in the thread pool and returns a `FaceAnalysisResult`.
3. `run_checks` produces the list of `CheckResult`.
4. When exactly one face is present, `crop_face_centered` produces the square crop, which is resized to `size` by `size`, encoded as PNG, and Base64-encoded. Otherwise `image_base64` is `null` and `crop_mode` is `null`.
5. The endpoint always returns `200 OK` with the JSON report.

### Example response

```json
{
  "passed": false,
  "crop_mode": "face",
  "output": {"width": 512, "height": 512, "format": "png",
             "image_base64": "iVBORw0K..."},
  "checks": [
    {"name": "exactly_one_face", "passed": true, "best_effort": false,
     "detail": "1 face detected", "measured": {"face_count": 1}},
    {"name": "frontal_pose", "passed": false, "best_effort": false,
     "detail": "yaw 23.4 degrees exceeds 15 degrees",
     "measured": {"yaw": 23.4, "pitch": 4.1, "roll": 2.0}},
    {"name": "no_sunglasses", "passed": true, "best_effort": true,
     "detail": "iris landmarks detected"}
  ],
  "warnings": ["no_headwear: forehead region partially occluded (best-effort)"]
}
```

## Error handling

- Unreadable or missing image: `422` with a clear message.
- Missing model file: fail fast during `lifespan`, so the service does not start.
- Zero or multiple faces: not an HTTP error; a normal report with `passed=false` and `image_base64=null`.
- `size` out of bounds: `422` from FastAPI validation.

## Concurrency

- One landmarker instance lives on the app, created in `lifespan`.
- `analyze` holds a `threading.Lock` and is dispatched with `anyio.to_thread.run_sync`, so the async event loop is never blocked.

## Testing (test-driven)

- Unit, fast, no MediaPipe: each check against a synthetic `CheckContext`; `crop_face_centered` against a dummy image and geometry.
- Integration, slow, real MediaPipe: `analyze` over `tests/test-images/*.jpg`; one endpoint test via `httpx` / `TestClient`.
- Response models: schema validation of the report.

## Dependencies and support window

- Add `mediapipe` and `numpy`.
- `opencv-python` can be dropped, since only the removed Haar cascade used it.
- Support caveat: `mediapipe` typically ships wheels up to Python 3.12, while `requires-python` is `>=3.10`.
  The implementation plan resolves this against the current PyPI state, either by capping the tox matrix at 3.12 or by making `mediapipe` an optional extra.

## Documentation follow-up

After implementation, extend the `docs/` tree:

- A reference entry for `/validate_and_crop/`.
- A how-to guide "validate a portrait photo".

## Open questions for the plan

- Confirm the current `mediapipe` Python version ceiling on PyPI and pick the tox strategy.
- Confirm how the `face_landmarker.task` asset is packaged (setuptools package data) and licensed for redistribution.
