from .checks import CheckContext
from .checks import overall_passed
from .checks import run_checks
from .checks import warnings_from
from .crop_utils import crop_face_centered
from .face_analysis import FaceAnalyzer
from .models import AppleWalletImageDefinitions
from .models import AppleWalletImageDefinitionsLiteral
from .models import AspectRatioEnum
from .models import GoogleWalletImageDefinitions
from .models import GoogleWalletImageDefinitionsLiteral
from .models import ImageSize
from .models import MaskTypeEnum
from .settings import get_settings
from .validation_models import OutputImage
from .validation_models import ValidationReport
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from importlib.metadata import version
from PIL import Image
from PIL import ImageDraw
from PIL import UnidentifiedImageError
from starlette.background import BackgroundTask
from typing import Annotated
from typing import Literal

import anyio
import base64
import io
import os
import pathlib
import tempfile
import uvicorn


logger.setLevel("DEBUG")

__version__ = version("edutap.image_api")
BASE_DIR = pathlib.Path(__file__).parent.resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Start eduTAP Image API Service")
    settings = get_settings()
    app.state.face_analyzer = FaceAnalyzer(settings.model_path)
    yield
    app.state.face_analyzer.close()
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
    # breakpoint()
    logger.debug("Filename: %s", file.filename)
    logger.debug("Filesize: %s", file.size)
    logger.debug("File Headers: %s", file.headers)
    logger.debug("Mask: %s", mask)
    logger.debug("Aspect Ratio: %s", aspect_ratio)
    logger.debug("Height: %s", height)
    logger.debug("Width: %s", width)
    logger.debug("Radius: %s", radius)

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


@app.post("/validate_and_crop/")
async def validate_and_crop(
    file: Annotated[UploadFile, File(description="Portrait image")],
    size: Annotated[
        int, Form(description="Output edge length in px", ge=16, le=4096)
    ] = 512,
) -> ValidationReport:
    try:
        image = Image.open(file.file)
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=422, detail=f"Unreadable image: {exc}")

    analyzer: FaceAnalyzer = app.state.face_analyzer
    result = await anyio.to_thread.run_sync(analyzer.analyze, image)

    ctx = CheckContext(result=result, settings=get_settings())
    checks = run_checks(ctx)

    crop_mode = None
    output = OutputImage(width=size, height=size, image_base64=None)
    if result.face_count == 1:
        cropped = crop_face_centered(
            image, result.faces[0].bbox, size, get_settings().crop_margin_factor
        )
        buffer = io.BytesIO()
        cropped.save(buffer, format="PNG", optimize=True)
        output.image_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        crop_mode = "face"

    return ValidationReport(
        passed=overall_passed(checks),
        crop_mode=crop_mode,
        checks=checks,
        warnings=warnings_from(checks),
        output=output,
    )


@app.post("/crop_wallet_assets_apple/", response_class=FileResponse)
async def crop_wallet_assets_file_apple(
    file: Annotated[UploadFile, File(description="Image File")],
    variant: Annotated[
        AppleWalletImageDefinitionsLiteral,
        Form(description="Wallet Type Asset Definition"),
    ],
):
    definition: ImageSize = AppleWalletImageDefinitions[variant]
    photo = Image.open(file.file)
    photo = photo.resize((definition.width, definition.height))
    output_file = tempfile.mkstemp(suffix=".png")[1]
    photo.show()

    return FileResponse(
        output_file,
        filename=definition.name,
        background=BackgroundTask(os.remove, output_file),
    )


@app.post("/crop_wallet_assets_google/", response_class=FileResponse)
async def crop_wallet_assets_file_google(
    file: Annotated[UploadFile, File(description="Image File")],
    variant: Annotated[
        GoogleWalletImageDefinitionsLiteral,
        Form(description="Wallet Type Asset Definition"),
    ],
):
    definition: ImageSize = GoogleWalletImageDefinitions[variant]
    photo = Image.open(file.file)
    photo = photo.resize((definition.width, definition.height))
    output_file = tempfile.mkstemp(suffix=".png")[1]

    return FileResponse(
        output_file,
        filename=definition.name,
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
