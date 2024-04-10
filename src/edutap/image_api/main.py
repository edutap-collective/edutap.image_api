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


@app.post("/crop/", response_class=FileResponse)
async def crop_file(
    file: UploadFile, *, mask: Annotated[str, MaskFormats] = MaskFormats.NONE
):
    print(file.filename)
    print(file.size)
    print(file.headers)
    print(mask)

    # return {"file-name": file.filename, "file-size": file.size}

    photo = Image.open(file.file)
    photo = photo.resize((1000, 1000))

    mask_circle_image = Image.new("RGBA", size=(1000, 1000))
    mask_circle = ImageDraw.Draw(mask_circle_image)
    mask_circle.ellipse((10, 10, 990, 990), fill="#ffffff")
    # mask_circle_image.save(f"output/{image_file}/mask_circle_1000x1000.png", format="PNG", optimize=True)

    mask_box_image = Image.new("RGBA", size=(1000, 1000))
    mask_box = ImageDraw.Draw(mask_box_image)
    mask_box.rounded_rectangle((0, 0, 1000, 1000), radius=100, fill="#ffffff")
    # mask_box_image.save(f"output/{image_file}/mask_box_1000x1000.png", format="PNG", optimize=True)

    background = Image.new("RGBA", size=(1000, 1000))

    output_file = tempfile.mkstemp(suffix=".png")[1]
    # breakpoint()

    result_circle = Image.composite(photo, background, mask_circle_image)
    result_circle.save(output_file, format="PNG", optimize=True)

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
