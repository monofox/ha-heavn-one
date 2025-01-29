"""Support for rd200 ble sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    CONF_ADDRESS,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .entity import HeavnOneEntity, HeavnOneSwitchEntity
from .heavn import HeavnOneDevice, HeavnOneProtocolHandler

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HeavnOneSensorEntityDescription[_T](SensorEntityDescription):
    """Entity description of a sensor entity with initial_value attribute."""

    initial_value: str | None = None
    command_type: str
    register_callback_func: Callable[
        [HeavnOneDevice], Callable[[Callable[[_T | None], None]], None]
    ]
    value_func: Callable[[_T | None], StateType]
    is_supported: Callable[[HeavnOneDevice], bool] = lambda device: True


SENSORS: tuple[HeavnOneSensorEntityDescription, ...] = (
    HeavnOneSensorEntityDescription[float](
        key="temperature",
        command_type=HeavnOneProtocolHandler.GET_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_func=lambda value: value.dataValue,
        register_callback_func=lambda device: device.register_sensor_callback,
        name="Temperature",
    ),
    HeavnOneSensorEntityDescription[float](
        key="humidity",
        command_type=HeavnOneProtocolHandler.GET_HUMIDITY,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value_func=lambda value: value.dataValue,
        register_callback_func=lambda device: device.register_sensor_callback,
        name="Humidity",
    ),
    HeavnOneSensorEntityDescription[int](
        key="pressure",
        command_type=HeavnOneProtocolHandler.GET_PRESSURE,
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MBAR,
        value_func=lambda value: value.dataValue,
        register_callback_func=lambda device: device.register_sensor_callback,
        name="Pressure",
    ),
    HeavnOneSensorEntityDescription[float](
        key="co2",
        command_type=HeavnOneProtocolHandler.GET_CO2,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        value_func=lambda value: value.dataValue,
        register_callback_func=lambda device: device.register_sensor_callback,
        name="CO2",
    ),
    HeavnOneSensorEntityDescription[float](
        key="co2_accuracy",
        command_type=HeavnOneProtocolHandler.GET_CO2_ACCURACY,
        device_class=None,
        native_unit_of_measurement=None,
        value_func=lambda value: value.dataValue,
        register_callback_func=lambda device: device.register_sensor_callback,
        name="CO2 Accuracy",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    device: HeavnOneDevice = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.info(f"Setup sensor values for device {device.address}")
    entities: list[SensorEntity] = [
        HeavnOneSensorEntity(device, entry, description)
        for description in SENSORS
        if description.is_supported(device)
    ]
    async_add_entities(entities)


class HeavnOneSensorEntity[_T](HeavnOneEntity, SensorEntity):
    """Representation of a sensor entity."""

    entity_description: SensorEntityDescription[_T]

    def __init__(
        self,
        device: HeavnOneDevice,
        entry: ConfigEntry,
        entity_description: HeavnOneSensorEntityDescription[_T],
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(
            device, entry, entity_description, unique_id_suffix=entity_description.key
        )
        self._attr_native_value = entity_description.initial_value

    async def async_added_to_hass(self) -> None:
        """Log sensor entity information."""
        _LOGGER.debug(
            "(%s) Setting up %s sensor entity",
            self.entry.data[CONF_ADDRESS],
            self.entity_description.key.replace("_", " "),
        )

        def async_callback(value: _T | None) -> None:
            """Update the sensor value."""
            self._attr_native_value = self.entity_description.value_func(value)
            self.async_write_ha_state()

        self.entity_description.register_callback_func(self.device)(
            self.entity_description.command_type, async_callback
        )
