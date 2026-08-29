from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

import pathlib


BASE_DIR = pathlib.Path(__file__).parent.resolve()
DEFAULT_MODEL_PATH = str(BASE_DIR / "assets" / "face_landmarker.task")


class Settings(BaseSettings):
    """Runtime configuration for image validation and cropping."""

    model_config = SettingsConfigDict(env_prefix="IMAGE_API_", env_file=".env")

    #: The path prefix this service is mounted under, or empty when it owns its host.
    #:
    #: A reverse proxy in front of this service may route by path rather than by
    #: host, and it may forward the prefix untouched instead of stripping it. Where
    #: it does, every route of this application sits one prefix deeper than the
    #: application believes, and the result is not a subtle misrouting -- it is a
    #: flat 404 on every endpoint, on ``/docs`` and on ``/openapi.json``, which is
    #: also how it was found: the OpenAPI document was unreachable at the deployed
    #: address.
    #:
    #: Measured against the versions this package locks (fastapi 0.141.1,
    #: starlette 1.6.0, uvicorn 0.52.4) with the prefix in use at LMU,
    #: ``/api/wallet/image-tools/v1``:
    #:
    #: ===================================  ==========  ===================
    #: Request                              unset       set
    #: ===================================  ==========  ===================
    #: ``POST <prefix>/validate_and_crop/``  404        200
    #: ``GET  <prefix>/docs``                404        200
    #: ``GET  <prefix>/openapi.json``        404        200
    #: ``POST /validate_and_crop/``          200        200
    #: ===================================  ==========  ===================
    #:
    #: The last row is why this is safe to set: starlette keeps serving the bare
    #: paths as well, so a health check or a sibling container calling the service
    #: directly inside the overlay network is unaffected.
    #:
    #: A setting rather than a constant, because the prefix belongs to a deployment
    #: and not to this package -- another institution mounts it elsewhere, and a
    #: development run mounts it nowhere. An empty default is therefore the honest
    #: one: it describes a service that owns its own root.
    root_path: str = ""

    min_face_area_ratio: float = 0.05
    max_face_area_ratio: float = 0.80
    max_center_offset_ratio: float = 0.15
    max_yaw_deg: float = 15.0
    max_pitch_deg: float = 15.0
    max_roll_deg: float = 10.0
    eye_open_threshold: float = 0.5
    crop_margin_factor: float = 1.6
    default_output_size: int = 512
    min_output_size: int = 16
    max_output_size: int = 4096
    model_path: str = DEFAULT_MODEL_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()
