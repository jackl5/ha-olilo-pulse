from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OliloPulseCoordinator

STATUS_UP_VALUES = {"up", "online", "active", "healthy", "ok", "true", "1"}


def _get_monitor_name(monitor: dict[str, Any]) -> str:
    return monitor.get("name") or monitor.get("title") or monitor.get("url") or monitor.get("target") or "Unknown"


def _is_monitor_up(monitor: dict[str, Any]) -> bool | None:
    status = monitor.get("status", monitor.get("state"))
    if status is None:
        return None
    return str(status).lower() in STATUS_UP_VALUES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OliloPulseCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[OliloPulseStatusSensor] = []
    for monitor_id in coordinator.data:
        entities.append(OliloPulseStatusSensor(coordinator, entry, monitor_id))

    async_add_entities(entities)


class OliloPulseStatusSensor(CoordinatorEntity[OliloPulseCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_translation_key = "status"

    def __init__(
        self,
        coordinator: OliloPulseCoordinator,
        entry: ConfigEntry,
        monitor_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._monitor_id = monitor_id
        monitor = coordinator.data[monitor_id]["monitor"]
        monitor_name = _get_monitor_name(monitor)

        self._attr_unique_id = f"{entry.entry_id}_{monitor_id}_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{monitor_id}")},
            "name": f"Olilo Pulse {monitor_name}",
            "manufacturer": "Olilo",
            "model": "Pulse Monitor",
            "entry_type": None,
        }

    @property
    def is_on(self) -> bool | None:
        if self._monitor_id not in self.coordinator.data:
            return None
        monitor = self.coordinator.data[self._monitor_id].get("monitor", {})
        return _is_monitor_up(monitor)
