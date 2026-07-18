---
myst:
  html_meta:
    "description": "Reference for the validate_and_crop endpoint of the eduTAP Image API Service."
    "property=og:description": "Reference for the validate_and_crop endpoint of the eduTAP Image API Service."
    "property=og:title": "validate_and_crop endpoint reference"
    "keywords": "eduTAP, image, API, biometric, validation, crop"
---

# `validate_and_crop` endpoint

The `validate_and_crop` endpoint validates a portrait photo against a set of biometric checks and returns a JSON report.
When the photo contains exactly one face, the report also embeds a face-centered, square crop of the photo as Base64.

## Request

| Property | Value |
|----------|-------|
| Method | `POST` |
| Path | `/validate_and_crop/` |
| Content type | `multipart/form-data` |

### Form parameters

| Name | Type | Required | Default | Constraints | Description |
|------|------|----------|---------|-------------|-------------|
| `file` | file | yes | — | — | The portrait image to validate. |
| `size` | integer | no | `512` | `16` to `4096` | Edge length in pixels of the square output image. |

## Response

The endpoint returns `200 OK` with a `ValidationReport` object whenever the image is readable.
It never returns a non-`200` status to signal a failed check.

### `ValidationReport`

| Field | Type | Description |
|-------|------|-------------|
| `passed` | boolean | `true` when every hard check passed. Best-effort checks do not affect this value. |
| `crop_mode` | `"face"` or `null` | `"face"` when a crop was produced. `null` when no crop was produced. |
| `checks` | array of `CheckResult` | One entry per check, in the order the checks run. |
| `warnings` | array of string | One message per best-effort check that failed. |
| `output` | `OutputImage` | The output image metadata and payload. |

### `CheckResult`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The check identifier. See [Checks](#checks). |
| `passed` | boolean | Whether the check passed. |
| `best_effort` | boolean | `true` for heuristic checks whose result does not affect `passed`. |
| `detail` | string | A human-readable explanation of the result. |
| `measured` | object | The measured values the check used, keyed by name. |

### `OutputImage`

| Field | Type | Description |
|-------|------|-------------|
| `width` | integer | The output width in pixels. Equal to `size`. |
| `height` | integer | The output height in pixels. Equal to `size`. |
| `format` | string | The image format. Always `"png"`. |
| `image_base64` | string or `null` | The Base64-encoded PNG, or `null` when no crop was produced. |

## Checks

The endpoint runs seven checks.
Five are hard checks: they determine the value of `passed`.
Two are best-effort checks: they are heuristic, never change `passed`, and surface in `warnings` when they fail.

| `name` | Type | Passes when |
|--------|------|-------------|
| `exactly_one_face` | hard | The image contains exactly one face. |
| `face_size` | hard | The face area relative to the image area lies within the configured bounds. |
| `face_centered` | hard | The face center is within the configured offset from the image center. |
| `frontal_pose` | hard | The head yaw, pitch, and roll are each within their configured tolerances. |
| `eyes_open` | hard | The eye-blink score is below the configured threshold. |
| `no_sunglasses` | best-effort | Iris landmarks are present and the eye signals are plausible. |
| `no_headwear` | best-effort | The forehead region is visible and not at the image edge. |

Every hard check other than `exactly_one_face` first requires exactly one face.
When the image contains zero or more than one face, those checks report `passed: false` with the detail `requires exactly one face`.

The thresholds for these checks come from the service settings.
See [Configuration](#configuration).

## Crop behavior

A crop is produced only when the image contains exactly one face.
The crop is a square centered on the face, expanded by the configured margin factor, and resized to `size` by `size` pixels.
When the image does not contain exactly one face, `crop_mode` is `null` and `output.image_base64` is `null`.

## Status codes

| Status | Condition |
|--------|-----------|
| `200 OK` | The image was readable. The body is a `ValidationReport`. |
| `422 Unprocessable Entity` | The upload is not a readable image, or `size` is outside `16` to `4096`. |

## Configuration

The check thresholds and the crop margin come from environment variables with the prefix `IMAGE_API_`.

| Variable | Default | Used by |
|----------|---------|---------|
| `IMAGE_API_MIN_FACE_AREA_RATIO` | `0.05` | `face_size` |
| `IMAGE_API_MAX_FACE_AREA_RATIO` | `0.80` | `face_size` |
| `IMAGE_API_MAX_CENTER_OFFSET_RATIO` | `0.15` | `face_centered` |
| `IMAGE_API_MAX_YAW_DEG` | `15.0` | `frontal_pose` |
| `IMAGE_API_MAX_PITCH_DEG` | `15.0` | `frontal_pose` |
| `IMAGE_API_MAX_ROLL_DEG` | `10.0` | `frontal_pose` |
| `IMAGE_API_EYE_OPEN_THRESHOLD` | `0.5` | `eyes_open` |
| `IMAGE_API_CROP_MARGIN_FACTOR` | `1.6` | crop |
| `IMAGE_API_MODEL_PATH` | bundled `face_landmarker.task` | face analysis |

## Example response

```json
{
  "passed": false,
  "crop_mode": "face",
  "checks": [
    {"name": "exactly_one_face", "passed": true, "best_effort": false,
     "detail": "1 face(s) detected", "measured": {"face_count": 1}},
    {"name": "frontal_pose", "passed": false, "best_effort": false,
     "detail": "yaw 8.4, pitch 2.1, roll -18.9",
     "measured": {"yaw": 8.4, "pitch": 2.1, "roll": -18.9}}
  ],
  "warnings": ["no_headwear: forehead region reaches image edge (headwear?)"],
  "output": {"width": 512, "height": 512, "format": "png",
             "image_base64": "iVBORw0KGgo..."}
}
```
