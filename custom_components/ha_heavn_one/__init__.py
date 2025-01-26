"""The RD200 BLE integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from .heavn import HeavnOneBluetoothDeviceData, HeavnOneDevice

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import METRIC_SYSTEM
from bleak_retry_connector import close_stale_connections_by_address

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HEAVN One BLE device from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    address = entry.unique_id
    assert address is not None
    await close_stale_connections_by_address(address)
    
    ble_device = bluetooth.async_ble_device_from_address(hass, address)

    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find HEAVN One device with address {address}")

    async def _async_update_method() -> HeavnOneDevice:
        """Get data from HEAVN One BLE."""
        ble_device = bluetooth.async_ble_device_from_address(hass, address)
        ho = HeavnOneBluetoothDeviceData(_LOGGER)

        try:
            data = await ho.update_device(ble_device)
        except Exception as err:
            raise UpdateFailed(f"Unable to fetch data: {err}") from err

        return data

    coordinator = ActiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=_async_update_method,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
