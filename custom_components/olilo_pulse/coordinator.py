from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OliloPulseApi, OliloPulseApiError, OliloPulseAuthError
from .const import DEFAULT_SCAN_INTERVAL, DEFAULT_STATS_RANGE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OliloPulseCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api: OliloPulseApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            monitors = await self.api.async_get_monitors()
        except OliloPulseAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except OliloPulseApiError as err:
            raise UpdateFailed(f"API error: {err}") from err

        result: dict[str, Any] = {}

        for monitor in monitors:
            monitor_id = str(monitor.get("id", monitor.get("_id", "")))
            if not monitor_id:
                continue

            try:
                stats = await self.api.async_get_monitor_stats(
                    monitor_id, DEFAULT_STATS_RANGE
                )
            except OliloPulseApiError:
                _LOGGER.warning("Failed to fetch stats for monitor %s", monitor_id)
                stats = {}

            try:
                data = await self.api.async_get_monitor_data(monitor_id, "1h")
                latest_ping = data[-1] if data else {}
            except (OliloPulseApiError, IndexError):
                _LOGGER.warning("Failed to fetch data for monitor %s", monitor_id)
                latest_ping = {}

            result[monitor_id] = {
                "monitor": monitor,
                "stats": stats,
                "latest_ping": latest_ping,
            }

        return result
