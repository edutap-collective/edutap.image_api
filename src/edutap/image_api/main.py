from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Response
from fastapi.logger import logger
from fastapi.staticfiles import StaticFiles
from importlib.metadata import version

import fastapi_chameleon
import glob
import importlib
import pathlib
import uvicorn


logger.setLevel("DEBUG")

__version__ = version("edutap.demo_service")
BASE_DIR = pathlib.Path(__file__).parent.resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializing
    logger.info("Start eduTAP Image API Service")
    template_folder = str(BASE_DIR / "templates")
    fastapi_chameleon.global_init(template_folder, auto_reload=True)
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


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
async def read_root():
    return {"title": "eduTAP Image API Service"}


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


def main():
    uvicorn.run(
        "edutap.demo_service.main:app",
        host="127.0.0.1",
        port=9500,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    main()
