from contextlib import asynccontextmanager
from enum import auto
from enum import StrEnum
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from importlib.metadata import version
from PIL import Image
from PIL import ImageDraw
from pydantic import BaseModel
from starlette.background import BackgroundTask
from typing import Annotated
from typing import Literal

import os
import pathlib
import tempfile
import uvicorn


logger.setLevel("DEBUG")

__version__ = version("edutap.image_api")
BASE_DIR = pathlib.Path(__file__).parent.resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializing
    logger.info("Start eduTAP Image API Service")
    # template_folder = str(BASE_DIR / "templates")
    # fastapi_chameleon.global_init(template_folder, auto_reload=True)
    # Serve
    yield
    # Shutdown
    logger.info("Shutdown eduTAP Image API Service")


app = FastAPI(
    title="eduTAP Image API Service",
    description="A FastAPI bases Image API Service for eduTAP, to crop and manipulate images.",
    version=__version__,
    lifespan=lifespan,
)

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def read_root():
    return {"title": "eduTAP Image API Service"}


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


class ImageSize(BaseModel):
    name: str
    width: int
    height: int


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


@app.post("/crop/", response_class=FileResponse)
async def crop_file(
    file: Annotated[UploadFile, File(description="Image File")],
    mask: Annotated[MaskTypeEnum, Form(description="Mask Type")] = MaskTypeEnum.NONE,
    aspect_ratio: Annotated[
        AspectRatioEnum, Form(description="Aspect Ratio of result Image")
    ] = AspectRatioEnum.SQUARE,
    height: Annotated[int, Form(description="Height of result Image")] = 1000,
    width: Annotated[
        int | Literal["auto"], Form(description="Width of result Image")
    ] = "auto",
    radius: Annotated[
        int, Form(description="Radius of Mask Box, if mask == BOX")
    ] = 100,
):
    logger.debug(f"Filename: {file.filename}")
    logger.debug(f"Filesize: {file.size}")
    logger.debug(f"File Headers: {file.headers}")
    logger.debug(f"Mask: {mask}")
    logger.debug(f"Aspect Ratio: {aspect_ratio}")
    logger.debug(f"Height: {height}")
    logger.debug(f"Width: {width}")
    logger.debug(f"Radius: {radius}")

    # Note: When uncommenting, remove the response_class=FileResponse from the function signature, otherwise this will raise an error
    # return {"file-name": file.filename, "file-size": file.size}

    photo = Image.open(file.file)

    if width in ["auto", "AUTO"] and aspect_ratio == AspectRatioEnum.FREE:
        raise ValueError(
            "Key width-value is 'auto', which is not allowed for aspect_ratio: free"
        )
    elif width in ["auto", "AUTO"]:
        if aspect_ratio == AspectRatioEnum.SQUARE:
            width = height
        elif aspect_ratio == AspectRatioEnum.PORTRAIT_3x4:
            width = int(height / 4 * 3)

    else:
        # case where width is an actual int value and aspect_ratio is free
        pass
    assert isinstance(width, int)

    photo = photo.resize((width, height))
    mask_image = Image.new("RGBA", size=(width, height))

    if mask == MaskTypeEnum.CIRCLE:
        mask_circle = ImageDraw.Draw(mask_image)
        mask_circle.ellipse((0, 0, width, height), fill="#ffffff")
    elif mask == MaskTypeEnum.BOX:
        mask_box = ImageDraw.Draw(mask_image)
        mask_box.rounded_rectangle((0, 0, width, height), radius=radius, fill="#ffffff")
    elif mask == MaskTypeEnum.NONE:  # Default Case
        pass
    else:
        raise KeyError(f"Unknown Mask Type: {mask}")

    output_file = tempfile.mkstemp(suffix=".png")[1]
    # breakpoint()

    if mask in (MaskTypeEnum.CIRCLE, MaskTypeEnum.BOX):
        background = Image.new("RGBA", size=(width, height))
        result_image = Image.composite(photo, background, mask_image)
        result_image.save(output_file, format="PNG", optimize=True)
    else:
        photo.save(output_file, format="PNG", optimize=True)

    # breakpoint()
    return FileResponse(
        output_file,
        filename="mask.png",
        background=BackgroundTask(os.remove, output_file),
    )


def main():
    uvicorn.run(
        "edutap.image_api.main:app",
        host="127.0.0.1",
        port=9500,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    main()
