from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import logging
from typing import Any, Callable, Tuple, TypeVar, cast
import uuid

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak_retry_connector import establish_connection

from .handler import HeavnOneProtocolHandler

_LOGGER = logging.getLogger(__name__)

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])


class BleakCharacteristicMissing(BleakError):
    """Raised when a characteristic is missing from a service."""


class BleakServiceMissing(BleakError):
    """Raised when a service is missing."""


class BleakInvalidDevice(BleakError):
    """Raised when the found device is probably not an HeavnOne."""


UART_WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_READ_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


@dataclasses.dataclass
class HeavnOneDevice:
    """Response data with information about the HEAVN One device."""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    serial_number: str = ""
    identifier: str = ""
    address: str = ""
    rssi: int = 0
    connectable: bool = True

    def __init__(self):
        self._handler = HeavnOneProtocolHandler()
        self._send_queue = asyncio.Queue()
        self._callbacks = {}
        self.uuid = uuid.uuid4()
        _LOGGER.debug(f'(%s) New device object created: {str(self.uuid)}', self.address)

    @property
    def handler(self):
        return self._handler

    def poll_needed(self, last_poll_time: float | None) -> bool:
        """Return if poll is needed."""
        return False

    def handle_notify(self, handle: int, data: bytearray) -> None:
        """Helper for command events."""

        dataPoint = self._handler.handleResponse(data)
        if dataPoint is not None:
            with contextlib.suppress(KeyError):
                self._callbacks[dataPoint.cmd](dataPoint)

            # specific data should be updated directly here.
            if dataPoint.cmd == self._handler.GET_NAME:
                self.name = dataPoint.dataValue
            elif dataPoint.cmd == self._handler.GET_SERIAL_NUMBER:
                self.serial_number = dataPoint.dataValue
            elif dataPoint.cmd == self._handler.GET_VERSION:
                self.sw_version = dataPoint.dataValue
            elif dataPoint.cmd == self._handler.GET_MAIN_PCB_FIRMWARE_VERSION:
                self.hw_version = dataPoint.dataValue

        _LOGGER.debug("Got data: {:s}".format(str(dataPoint)))

    def register_sensor_callback(self, cmdtype: str, callback) -> None:
        self._callbacks[cmdtype] = callback

    async def connect(self, device: BLEDevice) -> None:
        self._client = await establish_connection(BleakClient, device, self.address, disconnected_callback=self.handle_disconnect)
        await self._client.start_notify(UART_READ_UUID, self.handle_notify)

    async def _check_complete(self):
        while not self.name or not self.serial_number or not self.hw_version or not self.sw_version:
            await asyncio.sleep(1)

    async def collect_device_info(self):
        self.queue_send(self._handler.reqVersion())
        self.queue_send(self._handler.reqName())
        self.queue_send(self._handler.reqSerialNumber())
        self.queue_send(self._handler.reqHwVersion())
        self._loop = asyncio.get_event_loop()
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.excp_handler)
        try:
            _LOGGER.info('Running main loop!')
            main_tasks = {
                asyncio.create_task(self.send_loop()),
                asyncio.create_task(self.check_loop()),
                asyncio.create_task(self._check_complete())
            }

            done, pending = await asyncio.wait(main_tasks, return_when=asyncio.FIRST_COMPLETED)
            _LOGGER.debug(f'Completed Tasks: {[(t._coro, t.result()) for t in done]}')
            _LOGGER.debug(f'Pending Tasks: {[t._coro for t in pending]}')

        except BleakError as e:
            _LOGGER.error(f'Bluetooth connection failed')
            _LOGGER.exception(e)
        except Exception as e:
            _LOGGER.exception(e)
        finally:
            _LOGGER.warning('Shutdown initiated')
            _LOGGER.info('Shutdown complete.')
            await self.disconnect()

    async def _collect_metrics(self):
        # on first connection, ask for a bunch of data....
        self.queue_send(self._handler.reqButtonStates())
        self.queue_send(self._handler.reqGetSunCycleTime())
        self.queue_send(self._handler.reqGetSunDownAndDawn())
        self.queue_send(self._handler.reqCoffeeRelaxActivity())
        self.queue_send(self._handler.reqVersion())
        self.queue_send(self._handler.reqName())
        self.queue_send(self._handler.reqSerialNumber())
        self.queue_send(self._handler.reqHwVersion())
        self.queue_send(self._handler.reqUtcTime())
        self.queue_send(self._handler.reqGetManualModeState())
        while True:
            self.queue_send(self._handler.reqGetMetrics())
            self.queue_send(self._handler.reqAirQualityLED())
            await asyncio.sleep(10)

    async def run(self) -> None:
        self._loop = asyncio.get_event_loop()
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.excp_handler)
        try:
            _LOGGER.info('Running main loop!')
            main_tasks = {
                asyncio.create_task(self.send_loop()),
                asyncio.create_task(self.check_loop()),
                #asyncio.create_task(self.uart.run_loop()),
                asyncio.create_task(self._collect_metrics())
            }

            done, pending = await asyncio.wait(main_tasks, return_when=asyncio.FIRST_COMPLETED)
            _LOGGER.debug(f'Completed Tasks: {[(t._coro, t.result()) for t in done]}')
            _LOGGER.debug(f'Pending Tasks: {[t._coro for t in pending]}')

        except BleakError as e:
            _LOGGER.error(f'Bluetooth connection failed')
            _LOGGER.exception(e)
        except Exception as e:
            _LOGGER.exception(e)
        finally:
            _LOGGER.warning('Shutdown initiated')
            _LOGGER.info('Shutdown complete.')
            await self.disconnect()


    def excp_handler(self, loop: asyncio.AbstractEventLoop, context):
        # Handles exception from other tasks (inside bleak disconnect, etc)
        # loop.default_exception_handler(context)
        _LOGGER.debug(f'Asyncio execption handler called {context["exception"]}')
        _LOGGER.exception(context["exception"])
        self.disconnect()

    async def disconnect(self) -> None:
        if self._client:
            await self._client.stop_notify(UART_READ_UUID)
            await self._client.disconnect()

    def handle_disconnect(self, client: BleakClient):
        _LOGGER.warning(f'Device {client.address} disconnected')
        self.stop_loop()

    async def send_loop(self):
        while True:
            data = await self._send_queue.get()
            if data is None:
                break # Let future end on shutdown
            #if not self.write_enabled:
            #    logging.warning(f'Ignoring unexpected write data: {data}')
            #    continue
            _LOGGER.debug('(%s) Sending: %s', self.address, data)
            await self._client.write_gatt_char(UART_WRITE_UUID, data, True)

    def stop_loop(self):
        logging.info('Stopping Bluetooth event loop')
        self._send_queue.put_nowait(None)

    def queue_send(self, data: bytes):
        self._send_queue.put_nowait(data)

    async def check_loop(self):
        while True:
            await asyncio.sleep(1)

    def update_from_advertisement(
        self,
        service_info: BLEDevice,
        change: AdvertisementData,
    ) -> None:
        self.rssi = service_info.rssi
        self.name = service_info.name
        self.connectable = service_info.connectable

    @classmethod
    def fromDevice(cls, device):
        self = cls()
        self.name = device.name
        self.address = device.address

        return self


class HeavnOneBluetoothDeviceData:

    def __init__(
        self,
        logger: logging.Logger,
    ):
        super().__init__()
        self.logger = logger
        self._command_data = None
        self._event = None
        self._handler = HeavnOneProtocolHandler()

    def handle_notify(self, _: Any, data: bytearray) -> None:
        """Helper for command events."""
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
                self.logger.warning(
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
    async def _setup_device(
        self, client: BleakClient, device: HeavnOneDevice
    ) -> HeavnOneDevice:
        self._event = asyncio.Event()
        try:
            await client.start_notify(UART_READ_UUID, self.handle_notify)
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
            raise BleakInvalidDevice(
                "No response on serial number request - probably not an HEAVN One"
            )

        device.serial_number = response.dataValue
        return device

    async def update_device(self, ble_device: BLEDevice) -> HeavnOneDevice:
        """Connects to the device through BLE and retrieves relevant data"""

        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        device = HeavnOneDevice()
        device.name = ble_device.name
        device.address = ble_device.address
        try:
            await device.connect(ble_device)
            await device.collect_device_info()
        except:  # noqa: E722
            pass

        await client.disconnect()

        return device
