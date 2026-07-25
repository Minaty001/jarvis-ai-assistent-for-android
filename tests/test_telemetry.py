import pytest
from jarvis.pipelines.telemetry import TelemetryPipeline


@pytest.mark.asyncio
async def test_get_system_telemetry():
    telemetry = TelemetryPipeline()
    res = await telemetry.get_system_telemetry()
    assert "platform" in res
    assert "memory" in res
    assert "disk" in res
    assert "battery" in res
    assert res["status"] in ("NOMINAL", "WARNING")


@pytest.mark.asyncio
async def test_format_diagnostic_report():
    telemetry = TelemetryPipeline()
    report = await telemetry.format_diagnostic_report()
    assert "JARVIS System Telemetry" in report
    assert "RAM Usage" in report
