import pytest
from actions.android import DevicePipeline
from memory.storage import MemoryPipeline
from brain.intent import classify_intent


@pytest.mark.asyncio
async def test_copy_and_get_clipboard():
    device = DevicePipeline()
    res1 = await device.execute("copy_clipboard", {"text": "Jarvis Test Snippet"})
    assert isinstance(res1, str)

    res2 = await device.execute("get_clipboard", {})
    assert isinstance(res2, str)


@pytest.mark.asyncio
async def test_vibrate_and_toast():
    device = DevicePipeline()
    res_vib = await device.execute("vibrate_phone", {"duration": "100"})
    assert "vibrated" in res_vib or "unavailable" in res_vib

    res_toast = await device.execute("show_toast_msg", {"message": "Hello Android"})
    assert "Toast" in res_toast or "failed" in res_toast


@pytest.mark.asyncio
async def test_gps_and_media():
    device = DevicePipeline()
    res_gps = await device.execute("get_gps_location", {})
    assert isinstance(res_gps, str)

    res_media = await device.execute("media_control", {"action": "play"})
    assert "Media command" in res_media or "Could not" in res_media


@pytest.mark.asyncio
async def test_mobile_memory_pipeline(tmp_path):
    db_path = str(tmp_path / "test_mobile.db")
    memory = MemoryPipeline(db_path=db_path)
    await memory.initialize()

    row_id = await memory.save_clipboard("Confidential Code 1234")
    assert row_id > 0

    recent = await memory.get_recent_clipboard()
    assert len(recent) == 1
    assert recent[0]["content"] == "Confidential Code 1234"

    loc_id = await memory.save_location(35.6762, 139.6503, provider="gps")
    assert loc_id > 0

    last_loc = await memory.get_last_location()
    assert last_loc["latitude"] == 35.6762
    assert last_loc["longitude"] == 139.6503

    await memory.stop()


def test_mobile_intents_classification():
    intent, params = classify_intent("copy Hello World")
    assert intent == "copy_clipboard"
    assert params.get("text") == "hello world"

    intent2, _ = classify_intent("read the clipboard")
    assert intent2 == "get_clipboard"

    intent3, _ = classify_intent("vibrate device")
    assert intent3 == "vibrate_phone"

    intent4, params4 = classify_intent("show toast System Alert")
    assert intent4 == "show_toast_msg"
    assert params4.get("message") == "system alert"

    intent5, _ = classify_intent("where am i")
    assert intent5 == "get_gps_location"

    intent6, params6 = classify_intent("send text to 123456 with hello there")
    assert intent6 == "send_sms_msg"
    assert params6.get("number") == "123456"
    assert params6.get("message") == "hello there"
