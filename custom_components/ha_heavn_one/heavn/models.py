from __future__ import annotations
import asyncio
import dataclasses
import logging

from typing import Any, Callable, Tuple, TypeVar, cast

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .handler import HeavnOneProtocolHandler

_LOGGER = logging.getLogger(__name__)

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])

class BleakCharacteristicMissing(BleakError):
    """Raised when a characteristic is missing from a service."""


class BleakServiceMissing(BleakError):
    """Raised when a service is missing."""
    
class BleakInvalidDevice(BleakError):
    """Raised when the found device is probably not an HeavnOne"""

UART_WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_READ_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

@dataclasses.dataclass
class HeavnOneDevice:
    """Response data with information about the HEAVN One device"""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    serial_number: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )
    
class HeavnOneBluetoothDeviceData:
    
    def __init__(
        self,
        logger: Logger,
    ):
        super().__init__()
        self.logger = logger
        self._command_data = None
        self._event = None
        self._handler = HeavnOneProtocolHandler()
        
    def handle_notify(self, _: Any, data: bytearray) -> None:
        """Helper for command events"""
        self._command_data = data

        if self._event is None:
            return
        self._event.set()

    def disconnect_on_missing_services(func: WrapFuncType) -> WrapFuncType:
        """Define a wrapper to disconnect on missing services and characteristics.

        This must be placed after the retry_bluetooth_connection_error
        decorator.
        """

        async def _async_disconnect_on_missing_services_wrap(
            self, *args: Any, **kwargs: Any
        ) -> None:
            try:
                return await func(self, *args, **kwargs)
            except (BleakServiceMissing, BleakCharacteristicMissing) as ex:
                logger.warning(
                    "%s: Missing service or characteristic, disconnecting to force refetch of GATT services: %s",
                    self.name,
                    ex,
                )
                if self.client:
                    await self.client.clear_cache()
                    await self.client.disconnect()
                raise

        return cast(WrapFuncType, _async_disconnect_on_missing_services_wrap)
    
    @disconnect_on_missing_services
    async def _setup_device(self, client: BleakClient, device: HeavnOneDevice) -> HeavnOneDevice:
        self._event = asyncio.Event()
        try:
            await client.start_notify(
                UART_READ_UUID, self.handle_notify
            )
        except:
            self.logger.warn("_setup_device Bleak error 1")

        await client.write_gatt_char(UART_WRITE_UUID, self._handler.reqSerialNumber())
        
        # Wait for up to fice seconds to see if a
        # callback comes in.
        try:
            await asyncio.wait_for(self._event.wait(), 10)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting command data.")
        except:
            self.logger.warn("_setup_device Bleak error 2")

        await client.stop_notify(UART_READ_UUID)
        
        response = self._handler.handleResponse(self._command_data)
        if response is None:
            raise BleakInvalidDevice("No response on serial number request - probably not an HEAVN One")
        
        device.serial_number = response.dataValue
        return device
        
    async def update_device(self, ble_device: BLEDevice) -> HeavnOneDevice:
        """Connects to the device through BLE and retrieves relevant data"""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        device = HeavnOneDevice()
        device.name = ble_device.name
        device.address = ble_device.address
        device = await self._setup_device(client, device)

        await client.disconnect()

        return device
