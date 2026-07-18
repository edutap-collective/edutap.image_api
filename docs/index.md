---
myst:
  html_meta:
    "description": "Documentation for the eduTAP Image API Service, a FastAPI service that crops and transforms photos for id cards and wallet passes."
    "property=og:description": "Documentation for the eduTAP Image API Service, a FastAPI service that crops and transforms photos for id cards and wallet passes."
    "property=og:title": "eduTAP Image API Service"
    "keywords": "eduTAP, image, API, FastAPI, Apple Wallet, Google Wallet"
---

# eduTAP Image API Service

The eduTAP Image API Service is a FastAPI service that crops and transforms uploaded photos into the formats that identity cards and smart-device wallet passes need.

You upload an image, choose how it should be cropped and masked, and the service returns a ready-to-use PNG.
The service also knows the exact asset sizes that Apple Wallet and Google Wallet passes require, so you can generate those variants without looking up any dimensions yourself.

This documentation follows the [Diataxis](https://diataxis.fr/) framework.
Pick the section that matches what you need right now.

```{toctree}
:maxdepth: 2
:hidden:

tutorials/index
how-to/index
reference/index
explanation/index
```

## Tutorials

Start here if you are new to the service.

- {doc}`tutorials/crop-your-first-image` — install the service and crop an image from scratch.

## How-to guides

Task-focused directions for people who already know the basics.

- {doc}`how-to/validate-a-portrait-photo` — validate a portrait and retrieve the face-centered crop.

For operational tasks such as installing, running, deploying with Docker, and the demo frontend, see the project [README](https://github.com/edutap-eu/edutap.image_api#readme).

## Reference

The precise technical facts.

- {doc}`reference/validate-and-crop` — the validation endpoint, its report, and its checks.
- {doc}`reference/api-endpoints` — every endpoint, parameter, and response.
- {doc}`reference/image-definitions` — the enums and wallet asset sizes.

## Explanation

Background and design context.

- {doc}`explanation/architecture` — how the service is put together and why.
