"""The RD200 BLE integration."""
from __future__ import annotations

import logging

from bleak_retry_connector import close_stale_connections_by_address

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_register_callback,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .heavn import HeavnOneDevice

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH] #, Platform.LIGHT]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HEAVN One BLE device from a config entry."""
    assert entry.unique_id is not None
    address = entry.unique_id
    await close_stale_connections_by_address(address)

    ble_device = bluetooth.async_ble_device_from_address(hass, address=address.upper(), connectable=True)
    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find HEAVN One device with address {address}")

    device = HeavnOneDevice.fromDevice(ble_device)
    await device.connect(ble_device)
    await device.collect_device_info()

    # Register a callback that updates the BLEDevice in the library
    @callback
    def async_update_ble_device(
        service_info: BluetoothServiceInfoBleak, change: BluetoothChange
    ) -> None:
        """Update the BLEDevice."""
        _LOGGER.debug("(%s) New BLE device found", service_info.address)
        #device.set_ble_device(service_info.device, rssi=service_info.advertisement.rssi)

    entry.async_on_unload(
        async_register_callback(
            hass,
            async_update_ble_device,
            BluetoothCallbackMatcher(address=entry.data[CONF_ADDRESS]),
            BluetoothScanningMode.ACTIVE,
        )
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device
    _LOGGER.info("(%s) Updated device information, serial: %s", device.address, device.serial_number)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_create_background_task(hass, apply_fetch_data(hass, device, ble_device), ble_device.address)

    return True

async def apply_fetch_data(hass: HomeAssistant, device: HeavnOneDevice, ble_device: any) -> None:
    await device.connect(ble_device)
    await device.run()

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
