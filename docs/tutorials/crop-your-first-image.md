---
myst:
  html_meta:
    "description": "A beginner tutorial for the eduTAP Image API Service: install it and crop your first image."
    "property=og:description": "A beginner tutorial for the eduTAP Image API Service: install it and crop your first image."
    "property=og:title": "Crop your first image"
    "keywords": "eduTAP, image, API, tutorial, crop"
---

# Crop your first image

In this tutorial you install the eduTAP Image API Service, start it, and crop an image into a circular badge.
By the end you will have run the service, sent it a real request, and saved a result you can open.

You do not need to understand the internals yet.
Just follow each step and watch what happens.

## Install the service

First, clone the repository and enter it.

```console
git clone git@github.com:edutap-eu/edutap.image_api.git
cd edutap.image_api
```

Now create a virtual environment and install the package.

```console
uv venv
source .venv/bin/activate
uv pip install -U -e ".[test]"
```

The install pulls in the image libraries the service needs.
This can take a minute the first time.

## Start the service

Start the service with its console script.

```console
image_api
```

You should see log lines ending with a message that the service has started.
The service is now listening on `http://127.0.0.1:9500`.

Leave this terminal running and open a second one for the next steps.

## Open the interactive docs

In your browser, open `http://127.0.0.1:9500/docs`.

Notice that the page lists every endpoint, including `/crop/`.
This is the Swagger UI, generated automatically from the service.
You can send requests from here later, but in this tutorial you will use the command line.

## Crop an image

Pick any photo on your computer and note its path.
In the second terminal, send it to the `/crop/` endpoint and ask for a circular mask.

```console
curl -X POST http://127.0.0.1:9500/crop/ \
  -F "file=@/path/to/your/photo.jpg" \
  -F "mask=circle" \
  -F "aspect_ratio=square" \
  -F "height=512" \
  -o badge.png
```

Watch the first terminal.
You should see the service log the filename, the mask, and the size it received.
The `curl` command writes the result to `badge.png` in your current directory.

## Look at the result

Open `badge.png`.

You should see your photo resized to a 512 by 512 square with the corners outside the circle made transparent.
That transparency is the circular mask you asked for.

You have now installed the service, started it, and cropped your first image.

## Where to go next

Try changing the request and running it again.

- Set `mask=box` and add `radius=60` to get a rounded-rectangle badge instead of a circle.
- Set `mask=none` to get a plain square with no transparency.

When you are ready to validate portrait photos against biometric criteria, continue with {doc}`/how-to/validate-a-portrait-photo`.
