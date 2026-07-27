---
myst:
  html_meta:
    "description": "How to validate a portrait photo and get a face-centered crop from the eduTAP Image API Service."
    "property=og:description": "How to validate a portrait photo and get a face-centered crop from the eduTAP Image API Service."
    "property=og:title": "Validate a portrait photo"
    "keywords": "eduTAP, image, API, biometric, validation, portrait"
---

# Validate a portrait photo

This guide shows you how to check whether a photo meets the biometric criteria for an identity card or a wallet pass, and how to retrieve the resulting face-centered crop.

## Send the photo

Post the image to the `validate_and_crop` endpoint as `multipart/form-data`.
Set `size` to the edge length you want for the square output.

```console
curl -X POST http://127.0.0.1:9500/validate_and_crop/ \
  -F "file=@portrait.jpg" \
  -F "size=512" \
  -o report.json
```

The service always answers with `200 OK` and a JSON report when the image is readable.
If the upload is not a readable image, or `size` is outside the range `16` to `4096`, the service answers with `422`.

## Read the result

Inspect the top-level `passed` field to decide whether the photo is acceptable.

- `passed` is `true` when every hard check passed.
- `passed` is `false` when any hard check failed.

To find out which checks failed, read the `checks` array.
Each entry has a `name`, a `passed` flag, and a `detail` string.

```console
jq '.passed, (.checks[] | select(.passed == false) | .name)' report.json
```

Best-effort checks for accessories, such as `no_sunglasses` and `no_headwear`, never change `passed`.
When one of them fails, read its message from the `warnings` array and treat it as advice, not a hard rejection.

```console
jq '.warnings' report.json
```

For the full list of checks and their meaning, see {doc}`/reference/validate-and-crop`.

## Save the cropped image

When the photo contains exactly one face, the report embeds a face-centered PNG in `output.image_base64`.
Decode it to a file.

```console
jq -r '.output.image_base64' report.json | base64 --decode > cropped.png
```

When the photo does not contain exactly one face, `output.image_base64` is `null` and no crop is produced.
In that case, `crop_mode` is also `null`, and the `exactly_one_face` check in the report tells you how many faces were detected.
