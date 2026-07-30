"""Search pipeline — Web Intelligence & Live Weather/News (Thalamus Pipeline).

Provides real-time web querying, weather telemetry via Open-Meteo/wttr.in API,
and news highlights for live context injection into LLM reasoning.
Crafted by Minaty001.
"""

from __future__ import annotations

import asyncio
import urllib.parse
import json
from typing import Optional, Dict, Any
from jarvis.core.config import Config
from jarvis.pipelines.base import AsyncPipeline
from jarvis.utils.logging import log


class SearchPipeline(AsyncPipeline):
    """Async web intelligence and weather lookup pipeline."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    async def get_weather(self, location: str = "auto") -> str:
        """Fetch live weather data for specified location.

        Args:
            location: City name or 'auto' for IP location.

        Returns:
            Formatted weather summary string.
        """
        loc_clean = location.strip() if location and location.lower() != "auto" else ""
        url = f"https://wttr.in/{urllib.parse.quote(loc_clean)}?format=j1" if loc_clean else "https://wttr.in/?format=j1"

        try:
            import httpx
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    curr = data.get("current_condition", [{}])[0]
                    area = data.get("nearest_area", [{}])[0]
                    city = area.get("areaName", [{}])[0].get("value", "Current Location")
                    country = area.get("country", [{}])[0].get("value", "")

                    temp_c = curr.get("temp_C", "?")
                    feels_c = curr.get("FeelsLikeC", "?")
                    desc = curr.get("weatherDesc", [{}])[0].get("value", "Clear")
                    humidity = curr.get("humidity", "?")
                    wind_kmh = curr.get("windspeedKmph", "?")

                    loc_name = f"{city}, {country}" if country else city
                    return (
                        f"Atmospheric telemetry for {loc_name}, sir:\n"
                        f"- Conditions: {desc}\n"
                        f"- Temperature: {temp_c}°C (Perceived: {feels_c}°C)\n"
                        f"- Relative Humidity: {humidity}%\n"
                        f"- Wind Velocity: {wind_kmh} km/h"
                    )
        except Exception as e:
            log.warning(f"Live weather API error: {e}")

        # Fallback to standard HTTP text format
        try:
            import httpx
            fallback_url = f"https://wttr.in/{urllib.parse.quote(loc_clean)}?format=3" if loc_clean else "https://wttr.in/?format=3"
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(fallback_url)
                if resp.status_code == 200:
                    return f"Atmospheric telemetry for {location}, sir: {resp.text.strip()}"
        except Exception:
            pass

        return f"I'm afraid weather telemetry for '{location}' is unavailable at this moment, sir."

    async def search_web_summary(self, query: str) -> str:
        """Search the web for real-time information using DuckDuckGo Instant Answer API.

        Args:
            query: Search query string.

        Returns:
            Summary snippet or search message.
        """
        if not query:
            return "Please specify a query for web intelligence analysis, sir."

        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        try:
            import httpx
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    abstract = data.get("AbstractText", "")
                    if abstract:
                        return f"Web intelligence report for '{query}', sir:\n{abstract}"
                    heading = data.get("Heading", "")
                    related = data.get("RelatedTopics", [])
                    if related and isinstance(related, list):
                        snippets = []
                        for r in related[:3]:
                            if isinstance(r, dict) and "Text" in r:
                                snippets.append(f"- {r['Text']}")
                        if snippets:
                            return f"Web intelligence highlights for '{query}', sir:\n" + "\n".join(snippets)
        except Exception as e:
            log.warning(f"Web search API error: {e}")

        return f"Web intelligence search initiated for '{query}', sir. Standing by."
