---
myst:
  html_meta:
    "description": "Reference for the HTTP endpoints of the eduTAP Image API Service."
    "property=og:description": "Reference for the HTTP endpoints of the eduTAP Image API Service."
    "property=og:title": "HTTP endpoints reference"
    "keywords": "eduTAP, image, API, endpoints, crop"
---

# HTTP endpoints

The service exposes the following endpoints.
The validation endpoint has its own page: see {doc}`/reference/validate-and-crop`.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check. |
| `GET` | `/openapi.json` | The OpenAPI schema. |
| `POST` | `/crop/` | Crop and mask an image to an aspect ratio and size. |
| `POST` | `/crop_wallet_assets_apple/` | Resize an image to an Apple Wallet asset size. |
| `POST` | `/crop_wallet_assets_google/` | Resize an image to a Google Wallet asset size. |
| `POST` | `/validate_and_crop/` | Validate a portrait and return a face-centered crop. |

## `GET /`

Returns the service title as JSON.

```json
{"title": "eduTAP Image API Service"}
```

## `POST /crop/`

Resizes an image to an aspect ratio and size, and optionally applies a transparency mask.
The request uses `multipart/form-data`.
The response is a PNG file.

### Form parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file` | file | — | The image to crop. |
| `mask` | string | `none` | The mask to apply: `none`, `circle`, or `box`. |
| `aspect_ratio` | string | `square` | The target aspect ratio. See values below. |
| `height` | integer | `1000` | The output height in pixels. |
| `width` | integer or `auto` | `auto` | The output width in pixels, or `auto` to derive it from `aspect_ratio`. |
| `radius` | integer | `100` | The corner radius in pixels, used only when `mask` is `box`. |

### Aspect ratio values

`square`, `landscape_3x2`, `landscape_4x3`, `landscape_16x9`, `landscape_16x10`, `portrait_3x4`, `free`.

```{important}
When `width` is `auto`, the service derives the width only for `aspect_ratio` values `square` (width equals height) and `portrait_3x4` (width equals three quarters of the height).
For `free`, you must pass an explicit `width`.
For the `landscape_*` values with `width` set to `auto`, the service does not yet derive the width, and the request fails.
Pass an explicit `width` for those ratios.
```

## `POST /crop_wallet_assets_apple/` and `POST /crop_wallet_assets_google/`

Resize an image to a named Apple Wallet or Google Wallet asset size.
The request uses `multipart/form-data` with a single `variant` field that names the asset.
For the list of variants and their pixel sizes, see {doc}`/reference/image-definitions`.

```{warning}
These two endpoints are experimental.
In the current release they resize the image but do not yet write the result to the returned file, so the response is not usable.
Do not rely on them in production until this is fixed.
Use {doc}`/reference/validate-and-crop` or `POST /crop/` for working image output.
```

## `POST /validate_and_crop/`

See {doc}`/reference/validate-and-crop`.
