---
myst:
  html_meta:
    "description": "How the eduTAP Image API Service is structured and why."
    "property=og:description": "How the eduTAP Image API Service is structured and why."
    "property=og:title": "About the architecture"
    "keywords": "eduTAP, image, API, architecture, MediaPipe"
---

# About the architecture

This page explains how the service is put together and why it is shaped this way.
It is background reading, not a set of instructions.

## Two families of operation

The service does two different jobs, and the endpoints reflect that split.

The first job is plain image shaping.
`POST /crop/` takes an aspect ratio, a size, and an optional mask, and returns a PNG.
It makes no assumptions about the content of the image.

The second job is portrait validation.
`POST /validate_and_crop/` assumes the image is a photo of a person and asks whether that photo is fit for an identity card or a wallet pass.
This job needs to understand the image, not just resize it, so it carries far more machinery.

## The validation pipeline

The validation feature is deliberately split into small units, each with one responsibility and a narrow interface.
This keeps every biometric rule testable on its own and makes the set of rules easy to extend.

- `face_analysis` wraps the machine-learning model.
  It turns an image into a neutral result object: how many faces are present, and for each face a bounding box, a head pose, and a set of expression scores.
  Nothing downstream knows that this data came from a particular model.
- `checks` turns that result object into a list of check results.
  Each check is a small function that reads the analysis and the settings and returns one verdict.
  The checks never touch the model or the HTTP layer.
- `crop_utils` turns an image and a bounding box into a square, face-centered crop.
- The endpoint in `main` orchestrates these units and owns the HTTP contract.

Because the model wrapper hides behind a neutral result object, the rest of the pipeline would survive a change of model.
Because the checks are independent functions collected in a list, adding a stricter biometric rule later means writing one function, not editing a large one.

## Why MediaPipe

Earlier code used an OpenCV Haar cascade, which can find a face box but tells you little about how the face is posed.
The validation feature needs more: whether the head is turned, whether the eyes are open, and where the iris sits.

The service uses Google MediaPipe Face Landmarker, which returns a dense mesh of facial landmarks, a head-pose matrix, and expression scores in one pass.
Those outputs map directly onto the checks: the pose matrix drives the frontal-pose check, the expression scores drive the eyes-open check, and the presence of iris landmarks drives the sunglasses heuristic.
The Haar cascade was removed because MediaPipe covers everything it did and much more.

## Hard checks and best-effort checks

The checks fall into two groups, and the distinction is intentional.

Hard checks answer questions the landmarks answer reliably: how many faces there are, how large and centered the face is, how it is posed, and whether the eyes are open.
These decide the overall `passed` verdict.

Best-effort checks answer questions the landmarks answer only weakly, such as whether the subject wears sunglasses or headwear.
There is no dedicated accessory model in this release, so these checks are heuristics built from the same landmark data.
Rather than pretend they are authoritative, the service marks them `best_effort`, keeps them out of the `passed` verdict, and reports their failures as warnings.
This way a weak signal informs the caller without silently rejecting a valid photo.
A dedicated classifier can later join the pipeline as an ordinary check without disturbing this design.

## Blocking work off the event loop

The model runs synchronous, CPU-bound inference, and the landmarker instance is not safe to call from several threads at once.
The service loads one landmarker during startup, guards each inference call with a lock, and dispatches the call to a worker thread with `anyio.to_thread.run_sync`.
The asynchronous event loop therefore stays responsive while a photo is analyzed.

## Configuration

Every threshold that a check compares against, and the crop margin, come from settings rather than literals scattered through the code.
The settings read from environment variables with the prefix `IMAGE_API_`, so an operator can tune the strictness of validation without touching the source.
See {doc}`/reference/validate-and-crop` for the list of variables.
