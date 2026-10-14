from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class OliloPulseApiError(Exception):
    pass


class OliloPulseAuthError(OliloPulseApiError):
    pass


class OliloPulseApi:
    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    async def _request(self, path: str, params: dict[str, str] | None = None) -> Any:
        url = f"{API_BASE_URL}{path}"
        try:
            async with self._session.get(
                url, headers=self._headers, params=params, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 401:
                    raise OliloPulseAuthError("Invalid API key")
                if resp.status == 403:
                    raise OliloPulseAuthError("API key forbidden")
                if resp.status == 429:
                    raise OliloPulseApiError("Rate limited")
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise OliloPulseApiError(f"Request failed: {err}") from err

    async def async_get_monitors(self) -> list[dict[str, Any]]:
        data = await self._request("/monitors")
        if isinstance(data, list):
            return data
        return data.get("monitors", data.get("data", []))

    async def async_get_monitor(self, monitor_id: str) -> dict[str, Any]:
        return await self._request(f"/monitors/{monitor_id}")

    async def async_get_monitor_data(
        self, monitor_id: str, range_str: str = "24h"
    ) -> list[dict[str, Any]]:
        data = await self._request(f"/monitors/{monitor_id}/data", {"range": range_str})
        if isinstance(data, list):
            return data
        return data.get("data", data.get("pings", []))

    async def async_get_monitor_stats(
        self, monitor_id: str, range_str: str = "24h"
    ) -> dict[str, Any]:
        return await self._request(f"/monitors/{monitor_id}/stats", {"range": range_str})

    async def async_validate(self) -> bool:
        await self.async_get_monitors()
        return True
