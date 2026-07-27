# eduTAP Image API Service

A FastAPI-based image service for eduTAP.
It crops and transforms uploaded photos into the exact formats that identity cards and smart-device wallet passes require.

The service targets two use cases:

- General cropping with an aspect ratio and an optional circle or rounded-box mask.
- Ready-made asset sizes for Apple Wallet and Google Wallet passes.

A small React demo frontend under [frontend/](frontend/) shows how a browser client can call the service.

## Features

- Resize and crop an uploaded image to a chosen aspect ratio and size.
- Apply a circular or rounded-rectangle transparency mask.
- Produce Apple Wallet asset variants (background, footer, icon, logo, thumbnail, strip) at `@1x`, `@2x`, and `@3x`.
- Produce Google Wallet asset variants (logo, wide logo, hero, full-width, barcode overlays).
- Return each result as a downloadable PNG.
- Serve an interactive OpenAPI schema and Swagger UI out of the box.

## Requirements

- Python 3.10 or newer (3.12 recommended).
- The Python packages listed in [pyproject.toml](pyproject.toml), installed automatically by the steps below.

## Quickstart

Clone the repository:

```console
git clone git@github.com:edutap-eu/edutap.image_api.git
cd edutap.image_api
```

Create a virtual environment and install the package with `uv`:

```console
uv venv
source .venv/bin/activate
uv pip install -U -e ".[test,typecheck,develop]"
```

Start the service:

```console
image_api
```

The service listens on `http://127.0.0.1:9500`.
Open `http://127.0.0.1:9500/docs` for the interactive Swagger UI.

## HTTP endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check that returns the service title. |
| `GET` | `/openapi.json` | The OpenAPI schema. |
| `POST` | `/crop/` | Crop and mask an image to an aspect ratio and size. |
| `POST` | `/crop_wallet_assets_apple/` | Resize an image to an Apple Wallet asset size. |
| `POST` | `/crop_wallet_assets_google/` | Resize an image to a Google Wallet asset size. |
| `POST` | `/validate_and_crop/` | Validate a portrait and return a face-centered crop. |

Crop an image with `curl`:

```console
curl -X POST http://127.0.0.1:9500/crop/ \
  -F "file=@photo.jpg" \
  -F "mask=circle" \
  -F "aspect_ratio=square" \
  -F "height=1000" \
  -o result.png
```

See [docs/reference/api-endpoints.md](docs/reference/api-endpoints.md) for the full parameter list.

## Docker deployment

Build and run the service together with a Traefik reverse proxy:

```console
DOMAIN=image-api.example.org docker compose up --build
```

See [docs/how-to/deploy-with-docker.md](docs/how-to/deploy-with-docker.md) for details.

## Demo frontend

The [frontend/](frontend/) directory contains a React and Vite demo UI.
See [docs/how-to/run-the-demo-frontend.md](docs/how-to/run-the-demo-frontend.md) to run it.

## Documentation

The full documentation lives in [docs/](docs/) and follows the [Diataxis](https://diataxis.fr/) framework:

- Tutorials — learn the service by cropping your first image.
- How-to guides — run the service, deploy it, and generate wallet assets.
- Reference — the HTTP API and the wallet asset definitions.
- Explanation — how the service is built and why.

Start at [docs/index.md](docs/index.md).

## License

Distributed under the European Union Public Licence 1.2 (EUPL 1.2).
See [LICENSE](LICENSE).
