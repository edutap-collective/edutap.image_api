from enum import auto
from enum import StrEnum

from pydantic import BaseModel
from typing import Literal



class MaskTypeEnum(StrEnum):
    NONE = auto()
    """No Mask"""
    CIRCLE = auto()
    """Circle Mask"""
    BOX = auto()
    """Box Mask"""


class AspectRatioEnum(StrEnum):
    SQUARE = auto()
    """Square (Aspect Ratio 1:1)"""
    LANDSCAPE_3x2 = auto()
    """Landscape (Aspect Ratio 3:2 (Width:Height))"""
    LANDSCAPE_4x3 = auto()
    """Landscape (Aspect Ratio 4:3 (Width:Height))"""
    LANDSCAPE_16x9 = auto()
    """Landscape (Aspect Ratio 16:9 (Width:Height))"""
    LANDSCAPE_16x10 = auto()
    """Landscape (Aspect Ratio 16:10 (Width:Height))"""
    PORTRAIT_3x4 = auto()
    """Portrait (Aspect Ratio 3:4 (Width:Height))"""
    FREE = auto()
    """No predefined Aspect Ratio, width and height must be defined manually)"""


class ImageSize(BaseModel):
    name: str
    width: int
    height: int | Literal["auto"] = "auto"
    min_width: int | None = None
    max_width: int | None = None


AppleWalletBackgroundImage = ImageSize(name="background.png", width=180, height=220)
AppleWalletBackground2Image = ImageSize(
    name="background@2x.png", width=180 * 2, height=220 * 2
)
AppleWalletBackground3Image = ImageSize(
    name="background@3x.png", width=180 * 3, height=220 * 3
)

AppleWalletFooterImage = ImageSize(name="footer.png", width=286, height=15)
AppleWalletFooter2Image = ImageSize(name="footer@2x.png", width=286 * 2, height=15 * 2)
AppleWalletFooter3Image = ImageSize(name="footer@3x.png", width=286 * 3, height=15 * 3)

AppleWalletIconImage = ImageSize(name="icon.png", width=29, height=29)
AppleWalletIcon2Image = ImageSize(name="icon@2x.png", width=29 * 2, height=29 * 2)
AppleWalletIcon3Image = ImageSize(name="icon@3x.png", width=29 * 3, height=29 * 3)

AppleWalletLogoImage = ImageSize(name="logo.png", width=160, height=50)
AppleWalletLogo2Image = ImageSize(name="logo@2x.png", width=160 * 2, height=50 * 2)
AppleWalletLogo3Image = ImageSize(name="logo@3x.png", width=160 * 3, height=50 * 3)

AppleWalletThumbnailImage = ImageSize(name="thumbnail.png", width=90, height=90)
AppleWalletThumbnail2Image = ImageSize(
    name="thumbnail@2x.png", width=90 * 2, height=90 * 2
)
AppleWalletThumbnail3Image = ImageSize(
    name="thumbnail@3x.png", width=90 * 3, height=90 * 3
)

AppleWalletStripImageEventTicket = ImageSize(name="strip.png", width=375, height=98)
AppleWalletStrip2ImageEventTicket = ImageSize(
    name="strip@2x.png", width=375 * 2, height=98 * 2
)
AppleWalletStrip3ImageEventTicket = ImageSize(
    name="strip@3x.png", width=375 * 3, height=98 * 3
)

AppleWalletStripImageGiftCardAndCoupons = ImageSize(
    name="strip.png", width=375, height=144
)
AppleWalletStrip2ImageGiftCardAndCoupons = ImageSize(
    name="strip@2x.png", width=375 * 2, height=144 * 2
)
AppleWalletStrip3ImageGiftCardAndCoupons = ImageSize(
    name="strip@3x.png", width=375 * 3, height=144 * 3
)

AppleWalletStripImageOther = ImageSize(name="strip.png", width=375, height=123)
AppleWalletStrip2ImageOther = ImageSize(
    name="strip@2x.png", width=375 * 2, height=123 * 2
)
AppleWalletStrip3ImageOther = ImageSize(
    name="strip@3x.png", width=375 * 3, height=123 * 3
)

##

AppleWalletImageDefinitions = {
    "AppleWalletBackgroundImage": AppleWalletBackgroundImage,
    "AppleWalletBackground2Image": AppleWalletBackground2Image,
    "AppleWalletBackground3Image": AppleWalletBackground3Image,

    "AppleWalletFooterImage": AppleWalletFooterImage,
    "AppleWalletFooter2Image": AppleWalletFooter2Image,
    "AppleWalletFooter3Image": AppleWalletFooter3Image,

    "AppleWalletIconImage": AppleWalletIconImage,
    "AppleWalletIcon2Image": AppleWalletIcon2Image,
    "AppleWalletIcon3Image": AppleWalletIcon3Image,

    "AppleWalletLogoImage": AppleWalletLogoImage,
    "AppleWalletLogo2Image": AppleWalletLogo2Image,
    "AppleWalletLogo3Image": AppleWalletLogo3Image,

    "AppleWalletThumbnailImage": AppleWalletThumbnailImage,
    "AppleWalletThumbnail2Image": AppleWalletThumbnail2Image,
    "AppleWalletThumbnail3Image": AppleWalletThumbnail3Image,

    "AppleWalletStripImageEventTicket": AppleWalletStripImageEventTicket,
    "AppleWalletStrip2ImageEventTicket": AppleWalletStrip2ImageEventTicket,
    "AppleWalletStrip3ImageEventTicket": AppleWalletStrip3ImageEventTicket,

    "AppleWalletStripImageGiftCardAndCoupons": AppleWalletStripImageGiftCardAndCoupons,
    "AppleWalletStrip2ImageGiftCardAndCoupons": AppleWalletStrip2ImageGiftCardAndCoupons,
    "AppleWalletStrip3ImageGiftCardAndCoupons": AppleWalletStrip3ImageGiftCardAndCoupons,

    "AppleWalletStripImageOther": AppleWalletStripImageOther,
    "AppleWalletStrip2ImageOther": AppleWalletStrip2ImageOther,
    "AppleWalletStrip3ImageOther": AppleWalletStrip3ImageOther,
}

AppleWalletImageDefinitionsLiteral = Literal[
    "AppleWalletBackgroundImage",
    "AppleWalletBackground2Image",
    "AppleWalletBackground3Image",
    "AppleWalletFooterImage",
    "AppleWalletFooter2Image",
    "AppleWalletFooter3Image",
    "AppleWalletIconImage",
    "AppleWalletIcon2Image",
    "AppleWalletIcon3Image",
    "AppleWalletLogoImage",
    "AppleWalletLogo2Image",
    "AppleWalletLogo3Image",
    "AppleWalletThumbnailImage",
    "AppleWalletThumbnail2Image",
    "AppleWalletThumbnail3Image",
    "AppleWalletStripImageEventTicket",
    "AppleWalletStrip2ImageEventTicket",
    "AppleWalletStrip3ImageEventTicket",
    "AppleWalletStripImageGiftCardAndCoupons",
    "AppleWalletStrip2ImageGiftCardAndCoupons",
    "AppleWalletStrip3ImageGiftCardAndCoupons",
    "AppleWalletStripImageOther",
    "AppleWalletStrip2ImageOther",
    "AppleWalletStrip3ImageOther",
]

GoogleWalletLogoImage = ImageSize(name="logo.png", width=1200, height=1200)
GoogleWalletWideLogoImage = ImageSize(name="widelogo.png", width=1280, height=400)
# GoogleWalletWideLogoImage = ImageSize(name="widelogo.png", width=160 * 8, height=50 * 8)

GoogleWalletHeroImage = ImageSize(name="hero.png", width=1032, height=336)
GoogleWalletFullWidthImage = ImageSize(name="fullwidth.png", width=1860, height="auto")

GoogleWalletBarcodeAboveImage = ImageSize(name="barcode_above.png", width=780, height=80, max_width=1600, min_width=80)
GoogleWalletBarcodeBelowImage = ImageSize(name="barcode_below.png", width=1600, height=80, max_width=1600, min_width=80)

GoogleWalletImageDefinitions = {
    "GoogleWalletLogoImage": GoogleWalletLogoImage,
    "GoogleWalletWideLogoImage": GoogleWalletWideLogoImage,
    "GoogleWalletHeroImage": GoogleWalletHeroImage,
    "GoogleWalletFullWidthImage": GoogleWalletFullWidthImage,
    "GoogleWalletBarcodeAboveImage": GoogleWalletBarcodeAboveImage,
    "GoogleWalletBarcodeBelowImage": GoogleWalletBarcodeBelowImage,
}

GoogleWalletImageDefinitionsLiteral = Literal[
    "GoogleWalletLogoImage",
    "GoogleWalletWideLogoImage",
    "GoogleWalletHeroImage",
    "GoogleWalletFullWidthImage",
    "GoogleWalletBarcodeAboveImage",
    "GoogleWalletBarcodeBelowImage",
]
