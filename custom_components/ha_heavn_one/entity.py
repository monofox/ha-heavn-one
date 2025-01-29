"""Base entities for the Motionblinds Bluetooth integration."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription

from .heavn import HeavnOneDevice

_LOGGER = logging.getLogger(__name__)


class HeavnOneEntity(Entity):
    """Base class for HeavnOne entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    device: HeavnOneDevice
    entry: ConfigEntry

    def __init__(
        self,
        device: HeavnOneDevice,
        entry: ConfigEntry,
        entity_description: EntityDescription,
        unique_id_suffix: str | None = None,
    ) -> None:
        """Initialize the entity."""
        if unique_id_suffix is None:
            self._attr_unique_id = entry.data[CONF_ADDRESS]
        else:
            self._attr_unique_id = f"{entry.data[CONF_ADDRESS]}_{unique_id_suffix}"
        self.device = device
        self.entry = entry
        self.entity_description = entity_description
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, entry.data[CONF_ADDRESS])},
            manufacturer="HEAVN",
            model="",
            name=device.name,
            serial_number=device.serial_number,
            sw_version=device.sw_version,
            hw_version=device.hw_version
        )

    async def async_update(self) -> None:
        """Update state, called by HA if there is a poll interval and by the service homeassistant.update_entity."""
        _LOGGER.debug("(%s) Updating entity", self.entry.data[CONF_ADDRESS])
        await self.device.status_query()

class HeavnOneSwitchEntity(HeavnOneEntity, SwitchEntity):
    """Base class for HeavnOne Switch Entities."""

    def __init__(
        self,
        device: HeavnOneDevice,
        entry: ConfigEntry,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
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

        def async_callback(value: bool | None) -> None:
            """Update the sensor value."""
            self._attr_native_value = self.entity_description.value_func(value)
            self.async_write_ha_state()

        self.entity_description.register_callback_func(self.device)(
            self.entity_description.command_type, async_callback
        )

    @property
    def is_on(self):
        return self._attr_native_value

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        if self.entity_description.command_type == self.device.handler.GET_MANUAL_MODE_ENABLED:
            _LOGGER.debug("(%s) Try to turn (%s) on (via %s)", self.device.address, self.entity_description.command_type, str(self.device.uuid))
            self.device.queue_send(self.device.handler.reqSetManualMode(True))

    async def async_turn_off(self, **kwargs):
        """Turn the entity on."""
        if self.entity_description.command_type == self.device.handler.GET_MANUAL_MODE_ENABLED:
            self.device.queue_send(self.device.handler.reqSetManualMode(False))
