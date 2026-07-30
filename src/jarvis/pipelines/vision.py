"""Vision pipeline — image analysis & camera inspection (Occipital Cortex / Vision Region).

Provides visual sensing capabilities: photo capture via termux-camera-photo,
image metadata extraction, and visual context formatting.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import os
import base64
from typing import Optional
from jarvis.core.config import Config
from jarvis.pipelines.base import AsyncPipeline
from jarvis.utils.logging import log


class VisionPipeline(AsyncPipeline):
    """Async vision processing pipeline for Android / Termux."""

    def __init__(self, config: Config | None = None, photo_dir: str = "data/photos") -> None:
        super().__init__(config)
        self.photo_dir = photo_dir
        os.makedirs(self.photo_dir, exist_ok=True)

    async def capture_photo(self, camera_id: int = 0) -> str:
        """Capture a photo using Termux camera API.

        Args:
            camera_id: Camera index (0 for back, 1 for front).

        Returns:
            File path of captured image or error message string.
        """
        output_path = os.path.join(self.photo_dir, f"capture_{camera_id}.jpg")
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-camera-photo",
                "-c",
                str(camera_id),
                output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0 and os.path.exists(output_path):
                log.info(f"Photo captured successfully: {output_path}")
                return output_path
            err = stderr.decode(errors="replace").strip()
            log.warning(f"termux-camera-photo failed: {err}")
            return f"ERROR: Could not capture photo. {err}"
        except FileNotFoundError:
            return "ERROR: termux-camera-photo binary not found. Please install termux-api."
        except Exception as e:
            return f"ERROR: Photo capture failed: {e}"

    async def inspect_image(self, image_path: str) -> dict:
        """Inspect image file size, existence, and encode to base64 for LLM.

        Args:
            image_path: Path to local image file.

        Returns:
            Dict containing image metadata and base64 encoded data.
        """
        if not os.path.exists(image_path):
            return {"status": "error", "message": f"Image file not found: {image_path}"}

        try:
            size_bytes = os.path.getsize(image_path)
            with open(image_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

            return {
                "status": "success",
                "file_path": image_path,
                "size_bytes": size_bytes,
                "base64": b64_data,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to read image: {e}"}

    async def analyze_visual_target(self, query: str = "", image_path: Optional[str] = None) -> str:
        """High-level visual target scan routine.

        Captures a photo if image_path is not provided, then prepares visual telemetry.
        """
        target_path = image_path
        if not target_path or not os.path.exists(target_path):
            cap_result = await self.capture_photo(camera_id=0)
            if cap_result.startswith("ERROR"):
                return f"Visual sensor offline: {cap_result}"
            target_path = cap_result

        inspection = await self.inspect_image(target_path)
        if inspection.get("status") == "error":
            return f"Visual inspection failed: {inspection.get('message')}"

        size_kb = round(inspection.get("size_bytes", 0) / 1024, 1)
        prompt_info = f"Visual target acquired at '{target_path}' ({size_kb} KB), sir. Optical sensors reporting clear framing."
        if query:
            prompt_info += f" Visual analysis request: '{query}'."

        return prompt_info
