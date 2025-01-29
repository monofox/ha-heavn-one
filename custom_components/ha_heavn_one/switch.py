"""Support for rd200 ble sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant import config_entries
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .entity import HeavnOneSwitchEntity
from .heavn import HeavnOneDevice, HeavnOneProtocolHandler

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HeavnOneSwitchEntityDescription[_T](SwitchEntityDescription):
    """Entity description of a sensor entity with initial_value attribute."""

    initial_value: str | None = None
    command_type: str
    register_callback_func: Callable[
        [HeavnOneDevice], Callable[[Callable[[_T | None], None]], None]
    ]
    value_func: Callable[[_T | None], StateType]
    is_supported: Callable[[HeavnOneDevice], bool] = lambda device: True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    device: HeavnOneDevice = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.info(f"Setup sensor values for device {device.address}")
    entities: list[SwitchEntity] = []
    entities.append(
        HeavnOneSwitchEntity(
            device,
            entry,
            HeavnOneSwitchEntityDescription[bool](
                key="manual_mode",
                command_type=HeavnOneProtocolHandler.GET_MANUAL_MODE_ENABLED,
                device_class=None,
                value_func=lambda value: value.dataValue,
                register_callback_func=lambda device: device.register_sensor_callback,
                name="ManualMode",
            ),
        )
    )
    async_add_entities(entities)

