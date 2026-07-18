---
myst:
  html_meta:
    "description": "Reference for the image enums and wallet asset sizes of the eduTAP Image API Service."
    "property=og:description": "Reference for the image enums and wallet asset sizes of the eduTAP Image API Service."
    "property=og:title": "Image definitions reference"
    "keywords": "eduTAP, image, API, Apple Wallet, Google Wallet, sizes"
---

# Image definitions

This page lists the enumerations and the wallet asset sizes defined in `edutap.image_api.models`.

## Enumerations

### `MaskTypeEnum`

| Value | Meaning |
|-------|---------|
| `none` | No mask. |
| `circle` | Circular mask. |
| `box` | Rounded-box mask. |

### `AspectRatioEnum`

| Value | Ratio (width:height) |
|-------|----------------------|
| `square` | 1:1 |
| `landscape_3x2` | 3:2 |
| `landscape_4x3` | 4:3 |
| `landscape_16x9` | 16:9 |
| `landscape_16x10` | 16:10 |
| `portrait_3x4` | 3:4 |
| `free` | No fixed ratio. |

## Apple Wallet asset sizes

Each asset is defined at standard, `@2x`, and `@3x` resolutions.
The `@2x` and `@3x` sizes are the standard size multiplied by two and three.

| Asset | Standard (width x height) |
|-------|---------------------------|
| `background` | 180 x 220 |
| `footer` | 286 x 15 |
| `icon` | 29 x 29 |
| `logo` | 160 x 50 |
| `thumbnail` | 90 x 90 |
| `strip` (event ticket) | 375 x 98 |
| `strip` (gift card and coupons) | 375 x 144 |
| `strip` (other) | 375 x 123 |

The variant names accepted by `POST /crop_wallet_assets_apple/` follow the pattern `AppleWallet<Asset><Resolution>Image`, for example `AppleWalletBackgroundImage`, `AppleWalletBackground2Image`, and `AppleWalletBackground3Image`.

## Google Wallet asset sizes

| Variant | Width x height | Notes |
|---------|----------------|-------|
| `GoogleWalletLogoImage` | 1200 x 1200 | |
| `GoogleWalletWideLogoImage` | 1280 x 400 | |
| `GoogleWalletHeroImage` | 1032 x 336 | |
| `GoogleWalletFullWidthImage` | 1860 x auto | Height derived from the source. |
| `GoogleWalletBarcodeAboveImage` | 780 x 80 | Width between 80 and 1600. |
| `GoogleWalletBarcodeBelowImage` | 1600 x 80 | Width between 80 and 1600. |
