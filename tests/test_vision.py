import pytest
import os
import tempfile
from perception.vision import VisionPipeline


@pytest.mark.asyncio
async def test_inspect_nonexistent_image():
    vision = VisionPipeline()
    res = await vision.inspect_image("/invalid/path/image.jpg")
    assert res["status"] == "error"
    assert "not found" in res["message"]


@pytest.mark.asyncio
async def test_inspect_valid_image():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(b"fake_image_bytes")
        tmp_path = tmp.name

    try:
        vision = VisionPipeline()
        res = await vision.inspect_image(tmp_path)
        assert res["status"] == "success"
        assert res["size_bytes"] > 0
        assert "base64" in res
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@pytest.mark.asyncio
async def test_analyze_visual_target_fallback():
    vision = VisionPipeline()
    res = await vision.analyze_visual_target(query="Scan room", image_path="/invalid/img.jpg")
    assert "Visual" in res
