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
        key="avgLatency",
        translation_key="avg_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="minLatency",
        translation_key="min_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="maxLatency",
        translation_key="max_latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="avgPacketLoss",
        translation_key="packet_loss",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="uptimePercent",
        translation_key="uptime",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="totalPings",
        translation_key="total_pings",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OliloPulseCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[OliloPulseSensor] = []
    for monitor_id in coordinator.data:
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

        self._attr_unique_id = f"{entry.entry_id}_{monitor_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{monitor_id}")},
            "name": f"Olilo Pulse {monitor['name']}",
            "manufacturer": "Olilo",
            "model": "Pulse Monitor",
            "entry_type": None,
        }

    @property
    def native_value(self) -> float | None:
        if self._monitor_id not in self.coordinator.data:
            return None
        stats = self.coordinator.data[self._monitor_id].get("stats", {})
        val = stats.get(self.entity_description.key)
        if val is None:
            return None
        return round(float(val), 3)
