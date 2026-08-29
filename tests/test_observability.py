"""What the service reports, and when it stops paying for reporting nobody collects.

The wiring itself lives in `edutap.observability_settings` and is tested there. What
these tests hold is this package's half of the contract: that the call happens at all,
that it happens before anything else resolves settings, and that instrumentation is
gated on there actually being a receiver.
"""

from edutap.image_api import main
from edutap.observability_settings import OTLP_ENDPOINT_VARIABLE
from importlib.metadata import version

import pytest


def test_service_names_itself_by_its_distribution():
    """One spelling across a span, a log line and the installed distribution."""
    assert main.SERVICE_NAME == "edutap.image_api"
    assert version(main.SERVICE_NAME) == main.__version__


def test_observability_is_installed_at_import():
    """The settings object exists before any request, not on first use.

    `install_observability` must run before the module resolves the settings the
    service needs -- the application object reads `Settings` for its root path. The
    observable trace of that ordering is that the module carries a resolved
    `observability` by the time anything can import it.
    """
    assert main.observability is not None


def test_observability_reads_the_shared_edutap_prefix(monkeypatch):
    """`EDUTAP_`, not this package's own `IMAGE_API_`.

    A deployment sets `EDUTAP_ENVIRONMENT` once for a whole stack and means the same
    thing in every eduTAP service. Reading it under a private name would make this
    service the one that quietly reports into the wrong environment.
    """
    monkeypatch.setenv("EDUTAP_ENVIRONMENT", "staging")
    assert type(main.observability)().environment == "staging"


class _Observability:
    """Stands in for the resolved settings, so the switch can be tested both ways."""

    def __init__(self, telemetry_enabled: bool):
        self.telemetry_enabled = telemetry_enabled


@pytest.mark.parametrize(
    ("telemetry_enabled", "endpoint", "expected"),
    [
        (True, "http://collector:4317", True),
        # The deliberate off switch, with a receiver present.
        (False, "http://collector:4317", False),
        # The common case on this estate today: reporting on, nothing listening.
        (True, "", False),
        (False, "", False),
    ],
)
def test_export_requires_both_the_switch_and_a_receiver(
    monkeypatch, telemetry_enabled, endpoint, expected
):
    """Instrumentation is work on every request; unexported spans are work wasted.

    The endpoint is read from the environment rather than from a field, because
    `OTEL_EXPORTER_OTLP_ENDPOINT` is what every OpenTelemetry SDK reads by itself.
    """
    monkeypatch.setattr(main, "observability", _Observability(telemetry_enabled))
    if endpoint:
        monkeypatch.setenv(OTLP_ENDPOINT_VARIABLE, endpoint)
    else:
        monkeypatch.delenv(OTLP_ENDPOINT_VARIABLE, raising=False)

    assert main.exports_to_a_collector() is expected
