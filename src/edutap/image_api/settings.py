from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

import pathlib


BASE_DIR = pathlib.Path(__file__).parent.resolve()
DEFAULT_MODEL_PATH = str(BASE_DIR / "assets" / "face_landmarker.task")


class Settings(BaseSettings):
    """Runtime configuration for image validation and cropping."""

    model_config = SettingsConfigDict(env_prefix="IMAGE_API_", env_file=".env")

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
