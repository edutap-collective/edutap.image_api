from pydantic import BaseModel
from pydantic import Field
from typing import Literal


class CheckResult(BaseModel):
    """Result of a single validation check."""

    name: str
    passed: bool
    best_effort: bool = False
    detail: str = ""
    measured: dict[str, float | int] = Field(default_factory=dict)


class OutputImage(BaseModel):
    """Metadata and payload of the processed image."""

    width: int
    height: int
    format: str = "png"
    image_base64: str | None = None


class ValidationReport(BaseModel):
    """Full report returned by the validate_and_crop endpoint."""

    passed: bool
    crop_mode: Literal["face"] | None = None
    checks: list[CheckResult]
    warnings: list[str] = Field(default_factory=list)
    output: OutputImage
