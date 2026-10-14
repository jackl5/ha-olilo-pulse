from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OliloPulseCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="avg_latency",
        translation_key="avg_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="min_latency",
        translation_key="min_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="max_latency",
        translation_key="max_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="jitter",
        translation_key="jitter",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="packet_loss",
        translation_key="packet_loss",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
)

STAT_KEY_MAP = {
    "avg_latency": ("avg_latency", "avgLatency", "avg", "average", "latency_avg", "mean"),
    "min_latency": ("min_latency", "minLatency", "min", "latency_min"),
    "max_latency": ("max_latency", "maxLatency", "max", "latency_max"),
    "jitter": ("jitter", "avg_jitter", "avgJitter", "jitter_avg"),
    "packet_loss": ("packet_loss", "packetLoss", "loss", "packet_loss_pct"),
    "uptime": ("uptime", "uptime_pct", "uptimePercentage", "availability"),
}


def _extract_stat(stats: dict[str, Any], key: str) -> float | None:
    candidates = STAT_KEY_MAP.get(key, (key,))
    for candidate in candidates:
        val = stats.get(candidate)
        if val is not None:
            try:
                return round(float(val), 3)
            except (ValueError, TypeError):
                continue
    return None


def _get_monitor_name(monitor: dict[str, Any]) -> str:
    return monitor.get("name") or monitor.get("title") or monitor.get("url") or monitor.get("target") or "Unknown"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OliloPulseCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[OliloPulseSensor] = []
    for monitor_id, monitor_data in coordinator.data.items():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                OliloPulseSensor(coordinator, entry, monitor_id, description)
            )

    async_add_entities(entities)


class OliloPulseSensor(CoordinatorEntity[OliloPulseCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OliloPulseCoordinator,
        entry: ConfigEntry,
        monitor_id: str,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._monitor_id = monitor_id
        monitor = coordinator.data[monitor_id]["monitor"]
        monitor_name = _get_monitor_name(monitor)

        self._attr_unique_id = f"{entry.entry_id}_{monitor_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{monitor_id}")},
            "name": f"Olilo Pulse {monitor_name}",
            "manufacturer": "Olilo",
            "model": "Pulse Monitor",
            "entry_type": None,
        }

    @property
    def native_value(self) -> float | None:
        if self._monitor_id not in self.coordinator.data:
            return None
        stats = self.coordinator.data[self._monitor_id].get("stats", {})
        return _extract_stat(stats, self.entity_description.key)
