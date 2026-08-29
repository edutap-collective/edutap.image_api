---
myst:
  html_meta:
    "description": "Reference for the environment variables that configure the eduTAP Image API Service."
    "property=og:description": "Reference for the environment variables that configure the eduTAP Image API Service."
    "property=og:title": "Configuration reference"
    "keywords": "eduTAP, image, API, configuration, environment, observability"
---

(configuration-reference)=

# Configuration

The service reads its configuration from environment variables.
It also reads a `.env` file in the working directory of the process.
An environment variable takes precedence over the same name in `.env`.

Two prefixes are in use, and they belong to different owners.
`IMAGE_API_` names the settings this package defines.
`EDUTAP_` names the settings that `edutap.observability_settings` defines and that mean the same thing in every eduTAP service.

## Service settings

These variables use the prefix `IMAGE_API_`.
Every value is optional and falls back to the default shown.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `IMAGE_API_ROOT_PATH` | string | *(empty)* | The path prefix a proxy mounts the service under. |
| `IMAGE_API_MIN_FACE_AREA_RATIO` | float | `0.05` | Smallest share of the image the face may occupy. |
| `IMAGE_API_MAX_FACE_AREA_RATIO` | float | `0.80` | Largest share of the image the face may occupy. |
| `IMAGE_API_MAX_CENTER_OFFSET_RATIO` | float | `0.15` | Largest permitted offset of the face from the image center. |
| `IMAGE_API_MAX_YAW_DEG` | float | `15.0` | Largest permitted head rotation around the vertical axis, in degrees. |
| `IMAGE_API_MAX_PITCH_DEG` | float | `15.0` | Largest permitted head rotation around the lateral axis, in degrees. |
| `IMAGE_API_MAX_ROLL_DEG` | float | `10.0` | Largest permitted head tilt, in degrees. |
| `IMAGE_API_EYE_OPEN_THRESHOLD` | float | `0.5` | Score at or above which an eye counts as open. |
| `IMAGE_API_CROP_MARGIN_FACTOR` | float | `1.6` | Factor by which the crop extends beyond the detected face box. |
| `IMAGE_API_DEFAULT_OUTPUT_SIZE` | integer | `512` | Edge length in pixels when the request names none. |
| `IMAGE_API_MIN_OUTPUT_SIZE` | integer | `16` | Smallest accepted output edge length in pixels. |
| `IMAGE_API_MAX_OUTPUT_SIZE` | integer | `4096` | Largest accepted output edge length in pixels. |
| `IMAGE_API_MODEL_PATH` | string | bundled asset | Path to the MediaPipe face landmarker model. |

(configuration-root-path)=

## Root path

`IMAGE_API_ROOT_PATH` is the path prefix under which a reverse proxy publishes the service.
Set it to the prefix the proxy forwards, including the leading slash and without a trailing slash, for example `/api/wallet/image-tools/v1`.
Leave it empty when the service owns its own root.

You must set it when the proxy routes by path prefix and forwards that prefix unchanged.
The prefix then reaches the application, and the application serves its routes one level above it.

```{warning}
Without a matching root path, every endpoint answers `404` under the published address, including `/docs` and `/openapi.json`.
```

The value also appears in the `servers` entry of the generated OpenAPI document.
A client generated from that document therefore calls the published address rather than the bare one.

The bare paths remain reachable when a root path is set.
A health check or a sibling container that addresses the service directly is unaffected.

## Observability settings

These variables use the prefix `EDUTAP_`.
Every value is optional.
The service installs error reporting, tracing, and structured logging before it resolves any other setting.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EDUTAP_ENVIRONMENT` | string | `production` | Label on every error report and every exported span. |
| `EDUTAP_TELEMETRY_ENABLED` | boolean | `true` | Off switch for tracing, metrics, and log export. |
| `EDUTAP_LOG_LEVEL` | string | `INFO` | One of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`. |
| `EDUTAP_SENTRY_DSN` | string | *(unset)* | Sentry ingest address. An unset or empty value disables error reporting. |
| `EDUTAP_RELEASE` | string | *(unset)* | The artefact that is running, normally the image tag. Falls back to the package version. |
| `EDUTAP_PERSON_UID_MODE` | string | `pseudonym` | One of `pseudonym`, `plain`, `omit`. Decides whether a person may be named in exported data. |
| `EDUTAP_PSEUDONYM_SALT` | string | *(unset)* | HMAC key behind the person pseudonym. Without it there is no pseudonym. |

```{important}
A misspelled `EDUTAP_LOG_LEVEL` or `EDUTAP_PERSON_UID_MODE` aborts the start.
A value that is present but not legal must not be ignored, because ignoring it decides in silence what leaves the process.
```

## Trace export

The address of the collector is not an `EDUTAP_` setting.
The service reads `OTEL_EXPORTER_OTLP_ENDPOINT`, the variable every OpenTelemetry SDK reads by itself.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | string | *(unset)* | Address of the OTLP collector. |

Request instrumentation is installed only when `EDUTAP_TELEMETRY_ENABLED` is true **and** `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
Instrumentation patches the application whether or not a receiver exists, and a span that nobody collects is work performed on every request.

With tracing enabled and no endpoint set, the service writes spans to its console.
Structured logging is configured in every case, so a service without a collector remains readable.

The startup log states which of the two branches applies.

```{seealso}
{doc}`/reference/api-endpoints` for the paths the root path applies to.
```
