import pytest
from brain.telemetry import TelemetryPipeline


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
    assert "DIAGNOSTIC REPORT" in report
    assert "MEMORY CORES" in report
    assert "POWER SYSTEMS" in report
    assert "STORAGE BAY" in report
