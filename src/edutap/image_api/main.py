from contextlib import asynccontextmanager
from enum import StrEnum
from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.logger import logger
from fastapi.responses import FileResponse
from importlib.metadata import version
from PIL import Image
from PIL import ImageDraw
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


# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def read_root():
    return {"title": "eduTAP Image API Service"}


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


class MaskFormats(StrEnum):
    NONE = "No Mask"
    CIRCLE = "Circle Mask"
    BOX = "Box Mask"


class AspectRatios(StrEnum):
    FREE = "Free (no predefined Aspect Ratio, please define width and hight manually)"
    SQUARE = "Square (Aspect Ratio 1:1)"
    LANDSCAPE_3x2 = "Landscape (Aspect Ratio 3:2 (Width:Height))"
    LANDSCAPE_4x3 = "Landscape (Aspect Ratio 4:3 (Width:Height))"
    LANDSCAPE_16x9 = "Landscape (Aspect Ratio 16:9 (Width:Height))"
    LANDSCAPE_16x10 = "Landscape (Aspect Ratio 16:10 (Width:Height))"
    PORTRAIT_3x4 = "Portrait (Aspect Ratio 3:4 (Width:Height))"


@app.post("/crop/", response_class=FileResponse)
async def crop_file(
    file: UploadFile,
    *,
    mask: Annotated[Literal[MaskFormats.NONE, MaskFormats.CIRCLE, MaskFormats.BOX], MaskFormats] = MaskFormats.NONE,
    image_size: Annotated[Literal[AspectRatios.FREE, AspectRatios.SQUARE, AspectRatios.PORTRAIT_3x4], AspectRatios] = AspectRatios.SQUARE,
    height: Annotated[int, "Hight of result Image"] = 1000,
    width: Annotated[int | Literal["auto", "AUTO"], "Width of result Image"] = "auto",
    radius: Annotated[int, "Radius of Mask Box, if mask == BOX"] = 100,
):
    logger.debug(file.filename)
    logger.debug(file.size)
    logger.debug(file.headers)
    logger.debug(mask)

    # return {"file-name": file.filename, "file-size": file.size}

    photo = Image.open(file.file)

    if width in ["auto", "AUTO"] and image_size == AspectRatios.FREE:
        raise ValueError(
            "Key width-value is 'auto', which is not allowed for image_size: free"
        )
    elif width in ["auto", "AUTO"]:
        if image_size == AspectRatios.SQUARE:
            width = height
        elif image_size == AspectRatios.PORTRAIT_3x4:
            width = int(height / 4 * 3)

    else:
        # case where width is an actual int value and image_size is free
        pass
    assert isinstance(width, int)

    photo = photo.resize((width, height))
    mask_image = Image.new("RGBA", size=(width, height))

    if mask == MaskFormats.CIRCLE:
        mask_circle = ImageDraw.Draw(mask_image)
        mask_circle.ellipse((0, 0, width, height), fill="#ffffff")
    elif mask == MaskFormats.BOX:
        mask_box = ImageDraw.Draw(mask_image)
        mask_box.rounded_rectangle((0, 0, width, height), radius=radius, fill="#ffffff")
    elif mask == MaskFormats.NONE:  # Default Case
        pass
    else:
        raise KeyError(f"Unknown Mask Type: {mask}")

    output_file = tempfile.mkstemp(suffix=".png")[1]
    # breakpoint()

    if mask in (MaskFormats.CIRCLE, MaskFormats.BOX):
        background = Image.new("RGBA", size=(width, height))
        result_image = Image.composite(photo, background, mask_image)
        result_image.save(output_file, format="PNG", optimize=True)

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
