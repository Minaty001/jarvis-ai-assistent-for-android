import pytest
from jarvis.modules.autonomy import AutonomyPipeline
from jarvis.modules.telemetry import TelemetryPipeline


@pytest.mark.asyncio
async def test_autonomy_health_check():
    telemetry = TelemetryPipeline()
    autonomy = AutonomyPipeline(telemetry_pipeline=telemetry, check_interval_sec=1.0)

    res = await autonomy.check_health_now()
    assert "status" in res
    assert "battery_pct" in res
    assert "alert_triggered" in res


@pytest.mark.asyncio
async def test_autonomy_start_and_stop():
    telemetry = TelemetryPipeline()
    autonomy = AutonomyPipeline(telemetry_pipeline=telemetry, check_interval_sec=0.1)

    await autonomy.start()
    assert autonomy._running is True

    await autonomy.stop()
    assert autonomy._running is False
