import logging
import datetime

LOGGER = logging.getLogger('heavn')

class InvalidProtocolData(Exception):
    pass

class HeavnOneData():
    
    def __init__(self, cmd: str, dataType: str, dataValue: any):
        self.cmd = cmd
        self.dataType = dataType
        self.dataValue = dataValue


class HeavnOneProtocolHandler():
    """
    Not all commands are available to all systems.
    Very secret passwords (authentication): 
     - Developer: D3v3l0p3rM0d3
     - Merchant: M3rch4ntM0d3
     - Coworking: C0w0rk1n9M0d3
    """
    CO2 = "g"
    CO2_ACCURACY = "a"
    COMMAND_MANUAL = "C"
    COMMAND_QUARY_INTENSITY = "Q"
    COMMAND_SIDE = "^"
    COMMAND_SIDE_COUNT_GET = "^c"
    COMMAND_SIDE_MANUAL_GET = "^d"
    COMMAND_SIDE_MANUAL_SET = "^D"
    COMMAND_SIMULATE_BUTTON = "K"
    ENABLE_DFU_MODE = "#XX"
    FEATURE_ARRAY = "k"
    GET_ACTIVITY_TABLE_INDEX = "gT"
    GET_AIR_QUALITY_LED_ENABLED = "gA"
    GET_BLE_ID = "u"
    GET_BLUETOOTH_AUTO_OFF_ENABLED = "gF"
    GET_CHANNEL_DIRECT = "c"
    GET_CO2 = "qg"
    GET_CO2_ACCURACY = "qa"
    GET_COFFEE_RELAX_ACTIVITY = "W"
    GET_COWORKING_DEFAULT_INTENSITY = "gD"
    GET_COWORKING_MODE_ENABLE = "gC"
    GET_DEMO_MODE_ENABLED = "gM"
    GET_FEATURE_ARRAY = "qk"
    GET_GESTURE_SENSORS = "qi"
    GET_GESTURE_SENSORS_ENABLED = "gG"
    GET_HUMIDITY = "qh"
    GET_LAMP_ALIGNMENT = "gB"
    GET_LATITUDE = "b"
    GET_LIGHT_METRICS_DATAPOINT = "mgl"
    GET_LIGHT_METRICS_QUEUEU_POP = "mp2"
    GET_LIGHT_METRICS_QUEUE_LENGTH = "ml2"
    GET_LIGHT_ON_TIME = "gL"
    GET_LIGHT_SENSOR = "qL"
    GET_MESH_NUMBER_OF_SLAVES = "gXB"
    GET_MESH_NUMBER_OF_SLAVES_RESPONSE = "GXB"
    GET_LOADED_PRESET = "p"
    GET_LONGITUDE = "l"
    GET_MAIN_PCB_FIRMWARE_VERSION = "qf"
    GET_MANUAL_MODE_ENABLED = "e"
    GET_METRICS_GET = "mg"
    GET_METRICS_GET_CO2 = "mgg"
    GET_METRICS_GET_CO2_ACCURACY = "mga"
    GET_METRICS_GET_HUMIDITY = "mgh"
    GET_METRICS_GET_PRESSURE = "mgp"
    GET_METRICS_GET_TEMPERATURE = "mgt"
    GET_METRICS_GET_TIMESTAMP = "mgs"
    GET_METRICS_QUEUEU_LENGTH = "ml1"
    GET_METRICS_STARTUP_TIMESTAMP = "ms"
    GET_MOVEMENT = "qP"
    GET_NAME = "gN"
    GET_POWERED_ON_TIME = "gP"
    GET_PRESENCE = "o"
    GET_PRESET_DATA = "^s"
    GET_PRESET_NAME = "^n"
    GET_PRESSURE = "qp"
    GET_SERIAL_NUMBER_FROM_SECURE_STORAGE = "gS"
    GET_SERIAL_NUMBER = "u"
    GET_SUN_CYCLE_TIME = "Y"
    GET_SUN_DOWN_AND_DAWN = "X"
    GET_SYSTEM_CONFIGURATION = "qc"
    GET_TEMPERATURE = "qt"
    GET_TOP_MID_BOT = "s"
    GET_UTC_OFFSET = "d"
    GET_UTC_TIME = "h"
    GET_VERSION = "V"
    HUMIDITY = "h"
    LIGHT_SENSOR = "L"
    PIR = "P"
    PREFIX = "@"
    PRESSURE = "p"
    RECEIVE_RTC_TIME = "H"
    RESET_FLASH = "J"
    SERIAL_NUMBER_SECURE_STORAGE = "GS"
    SET_ACTIVITY_TABLE_INDEX = "GT"
    SET_AIR_QUALITY_LED_ENABLED = "GA"
    SET_BLUETOOTH_AUTO_OFF_ENABLED = "GF"
    SET_CHANNEL_DIRECT = "C"
    SET_COWORKING_DEFAULT_INTENSITY = "GD"
    SET_COWORKING_MODE_ENABLE = "GC"
    SET_DEMO_MODE_ENABLED = "GM"
    SET_GESTURE_SENSORS_ENABLED = "GG"
    SET_INTENSITY = "I"
    SET_LAMP_ALIGNMENT = "GB"
    SET_LATITUDE = "B"
    SET_LOADED_PRESET = "P"
    SET_LONGITUDE = "L"
    SET_MESH_ADD_SLAVE = "GXE"
    SET_MESH_REMOVE_SLAVES = "GXK"
    SET_METRICS_QUEUEU_POP = "mp1"
    SET_NAME = "GN"
    SET_PRESENCE = "O"
    SET_PRESET_DATA = "^S"
    SET_PRESET_NAME = "^N"
    SET_SIMULATE_ACTIVITY_LEVEL = "A"
    SET_SUN_CYCLE_TIME = "T"
    SET_UTC_OFFSET = "D"
    SET_UTC_TIME = "H"
    TEMPERATURE = "t"
    TOGGLE_MANUAL_MODE = "R"
    SIDES = ['up', 'bio', 'down']
    
    def reqCO2(self):
        return self._buildCommand(self.GET_CO2)
    
    def reqCO2Accuracy(self):
        return self._buildCommand(self.GET_CO2_ACCURACY)
    
    def reqAirQualityLED(self):
        return self._buildCommand(self.GET_AIR_QUALITY_LED_ENABLED)
    
    def reqLightSensor(self):
        return self._buildCommand(self.GET_LIGHT_SENSOR)
    
    def reqVersion(self):
        return self._buildCommand(self.GET_VERSION)
    
    def reqName(self):
        """Build command to request the devices name

        Returns:
            str: command
        """
        return self._buildCommand(self.GET_NAME)
    
    def reqSerialNumber(self):
        """Build command to request the devices serial number

        Returns:
            str: command
        """
        return self._buildCommand(self.GET_SERIAL_NUMBER)
    
    def reqUtcTime(self):
        return self._buildCommand(self.GET_UTC_TIME)
    
    def reqCoffeeRelaxActivity(self):
        return self._buildCommand(self.GET_COFFEE_RELAX_ACTIVITY)
    
    def reqSetUtcTime(self, dt=None):
        if not dt:
            dt = datetime.datetime.utcnow()
        pr = dt.strftime('%H%M%S')
        return self._buildCommand(self.SET_UTC_TIME, pr)
        
    def reqSetUtcOffset(self, utcOffset: int = 0):
        utcOffset += 0 if utcOffset >= 0 else 24
        utcOffsetStr = '{:0>2d}'.format(utcOffset)
        return self._buildCommand(self.SET_UTC_OFFSET, utcOffsetStr)
    
    def reqSetSunCycleTime(self, dt=None):
        if not dt:
            dt = datetime.datetime.now()
        # need to send in: HHmmssddMMyy
        pr = dt.strftime('%H%M%S%d%m%y')
        return self._buildCommand(self.SET_SUN_CYCLE_TIME, pr)
    
    def reqGetSunCycleTime(self):
        return self._buildCommand(self.GET_SUN_CYCLE_TIME)

    def reqGetSunDownAndDawn(self):
        return self._buildCommand(self.GET_SUN_DOWN_AND_DAWN)

    def reqGetMetrics(self):
        command = self.GET_METRICS_GET_CO2 + \
            self.PREFIX + \
            self.GET_METRICS_GET_CO2_ACCURACY + \
            self.PREFIX + \
            self.GET_METRICS_GET_TEMPERATURE + \
            self.PREFIX + \
            self.GET_METRICS_GET_PRESSURE + \
            self.PREFIX + \
            self.GET_METRICS_GET_HUMIDITY + \
            self.PREFIX + \
            self.GET_METRICS_GET_TIMESTAMP
        return self._buildCommand(command)
    
    def reqButtonStates(self):
        return self._buildCommand(self.GET_TOP_MID_BOT)
    
    def reqGetAllChannels(self, channel: int = None):
        # channels:
        # 0 = TopWW, 1 = TopNW, 2 = TopCW, 3 = MidWW, 4 = MidCW, 5 = MidBlue, 6 = BotWW, 7 = BotNW, 8 = BotCW
        commands = b''
        if channel is None:
            for channel in range(0, 11):
                commands += self._buildCommand(self.GET_CHANNEL_DIRECT, str(channel))
        else:
            commands = self._buildCommand(self.GET_CHANNEL_DIRECT, str(channel))
        return commands
    
    # services
    def reqTogglePower(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'XXXXXD')

    def reqToggleCoffee(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'DXXXXX')

    def reqToggleRelax(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'XDXXXX')

    def reqToggleLeft(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'XXXDXX')

    def reqToggleRight(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'XXDXXX')

    def reqToggleBio(self):
        return self._buildCommand(self.COMMAND_SIMULATE_BUTTON, 'XXXXDX')
    
    def reqSetManualMode(self, manualMode: bool = False):
        return self._buildCommand(
            self.COMMAND_MANUAL
        )
    
    def reqVideoMode(self):
        scene = [100, 60, 30, 15, 100, 65]
        # int(scene[(x * 2) + 1]) = temperature of side x
        # int(scene[(x * 2) + 0]) = intensity of side x
        # up = 1, bio = 2, down = 3
        # convert the index: up = 0; down = 2; bio = 1
        
        return self.reqManualScene(scene)
    
    def reqManualScene(self, scene):
        cmd = ''
        for s in range(0, self.SIDES):
            temp = int(scene[(s * 2) + 1])
            intensity = int(scene[(s * 2) + 0])
            cmd += self.PREFIX + self.COMMAND_SIDE_MANUAL_SET + self._padInteger(s, 2) + self._padInteger(intensity, 3) + self._padInteger(temp, 3)
            
        return self._buildCommand(cmd, skipPrefix=True) + self.reqSetManualMode(True)
    
    def reqSetPreset(self, scene):
        cmd = ''
        for s in range(0, self.SIDES):
            temp = int(scene[(s * 2) + 1])
            intensity = int(scene[(s * 2) + 0])
            cmd += self.PREFIX + self.SET_PRESET_DATA + '1' + str(s) + self._padInteger(intensity, 3) + self._padInteger(temp, 3)
            
        return self._buildCommand(cmd, skipPrefix=True) + self.reqSetManualMode(True)
    
    def reqSetPresetName(self, sceneName: str):
        if not sceneName:
            logging.error("Missing scene name!")
            return
        
        if len(sceneName) > 10:
            logging.warning("Scene name too long: {:s}".format(sceneName))
            sceneName = sceneName[:10]
            
        # FIXME: ensure, name is ascii.
        
        # pad it
        while len(sceneName) < 10:
            sceneName += ' '
        return self._buildCommand(
            self.SET_PRESET_NAME + '1' + sceneName
        )
        
    def reqGetPresetData(self):
        return self._buildCommand(
            self.PREFIX + self.GET_PRESET_DATA + '10' +
            self.PREFIX + self.GET_PRESET_DATA + '11' +
            self.PREFIX + self.GET_PRESET_DATA + '12',
            skipPrefix=True
        )
    
    def reqGetPresetName(self):
        return self._buildCommand(self.GET_PRESET_NAME + '1')
        
    def _buildCommand(self, cmd, parm=None, skipPrefix: bool = False):
        if not skipPrefix:
            cmd = self.PREFIX + cmd
        if parm:
            cmd += parm
        
        return cmd.encode('ascii')
    
    def _padInteger(self, value, digits):
        strValue = str(value)
        while len(strValue) < digits:
            strValue = '0' + strValue
            
        return strValue
    
    def handleResponse(self, value: bytearray):
        cmd = value.decode('ascii')
        if cmd[0] != '$':
            logging.warning("Got command without a response {:s}".format(str(value)))
            return None
        
        if cmd[1] == self.SET_INTENSITY:
            return self.onIntensityReceived(cmd[2:])
        elif cmd[1] == self.GET_TOP_MID_BOT:
            return self.onButtonStateReceived(cmd[2:])
        elif cmd[1] == self.GET_VERSION:
            return self.onVersion(cmd[2:])
        elif cmd[1:3] == self.GET_NAME:
            return self.onName(cmd[3:])
        elif cmd[1] == self.GET_SERIAL_NUMBER:
            return self.onSerialNumber(cmd[2:])
        elif cmd[1] == self.GET_COFFEE_RELAX_ACTIVITY:
            return self.onCoffeeRelaxActivityReceived(cmd[2:])
        elif cmd[1] == self.GET_LATITUDE:
            return self.onLatitudeReceived(cmd[2:])
        elif cmd[1] == self.GET_LONGITUDE:
            return self.onLongitudeReceived(cmd[2:])
        elif cmd[1] in [self.GET_PRESENCE, self.SET_PRESENCE]:
            return self.onPresenceReceived(cmd[2:])
        elif cmd[1] in [self.GET_SUN_CYCLE_TIME]:
            return self.onSunCycleTimeReceived(cmd[2:])
        elif cmd[1] == self.SET_SUN_CYCLE_TIME:
            return self.onUtcTimeReceived(cmd[2:])
        elif cmd[1] == self.GET_SUN_DOWN_AND_DAWN:
            return self.onSunDownAndDawnReceived(cmd[2:])
        elif cmd[1] == self.GET_UTC_OFFSET:
            return self.onUtcOffsetReceived(cmd[2:])
        elif cmd[1] == self.RECEIVE_RTC_TIME:
            return self.onUtcTimeReceived(cmd[2:])
        elif cmd[1] == self.SET_CHANNEL_DIRECT:
            return self.onChannelDirectReceived(cmd[2:])
        elif cmd[1:3] == self.GET_CO2:
            return self.onCO2Received(cmd[3:])
        elif cmd[1:4] == self.GET_METRICS_GET_CO2:
            return self.onCO2Received(cmd[4:])
        elif cmd[1:3] == self.GET_CO2_ACCURACY:
            return self.onCO2AccuracyReceived(cmd[3:])
        elif cmd[1:4] == self.GET_METRICS_GET_CO2_ACCURACY:
            return self.onCO2AccuracyReceived(cmd[4:])
        elif cmd[1:3] == self.GET_HUMIDITY:
            return self.onHumidity(cmd[3:])
        elif cmd[1:4] == self.GET_METRICS_GET_HUMIDITY:
            return self.onHumidity(cmd[4:])
        elif cmd[1:3] == self.GET_PRESSURE:
            return self.onPressure(cmd[3:])
        elif cmd[1:4] == self.GET_METRICS_GET_PRESSURE:
            return self.onPressure(cmd[4:])
        elif cmd[1:3] == self.GET_TEMPERATURE:
            return self.onTemperature(cmd[3:])
        elif cmd[1:4] == self.GET_METRICS_GET_TEMPERATURE:
            return self.onTemperature(cmd[4:])
        elif cmd[1:3] == self.GET_AIR_QUALITY_LED_ENABLED:
            return self.onAirQualityLEDReceived(cmd[3:])
        elif cmd[1:3] == self.GET_LIGHT_SENSOR:
            return self.onLightSensor(cmd[3:])
        elif cmd[1] == self.GET_MANUAL_MODE_ENABLED:
            return self.onManualMode(cmd[2:])
        elif cmd[1:3] == self.SET_PRESET_DATA:
            return self.onPresetData(cmd[3:])
        else:
            #raise Exception('Command unknown: {:s} / full: {:s}'.format(str(cmd[:2]), cmd))
            logging.error('Command unknown: {:s} / full: {:s}'.format(str(cmd[:2]), cmd))
            return None
    
    def onIntensityReceived(self, value):
        # three percentages: 100.030.095
        # sequence: right (down), bio, left (up)
        rightStr, bioStr, leftStr = value.split('.')
        right = int(rightStr)
        bio = int(bioStr)
        left = int(leftStr)
        self.onIntensityChanged(right, bio, left)

    def onButtonStateReceived(self, value):
        # 1111
        # 1 = on, 0 = off
        # 1st: left
        # 2nd: bio
        # 3rd: right
        butLeftEnabled = True if value[0] == '1' else False
        butBioEnabled = True if value[1] == '1' else False
        butRightEnabled = True if value[2] == '1' else False
        logging.info('Button state changed: up={:}, bio={:}, down={:}'.format(
            butLeftEnabled,
            butBioEnabled,
            butRightEnabled
        ))

    def onVersion(self, value):
        logging.info('Firmware version: {:s}'.format(value))
        self.firmwareVersion = value

    def onName(self, value):
        logging.info('Lamp name: {:s}'.format(value))
        self.name = value
        
        return HeavnOneData(self.GET_NAME, 'str', value)

    def onSerialNumber(self, value):
        logging.info('Serial number: {:s}'.format(value))
        self.serialNumber = value
        
        return HeavnOneData(self.GET_SERIAL_NUMBER, 'str', value)

    def onCoffeeRelaxActivityReceived(self, value):
        coffeeStep = int(value[0:1])
        relaxStep = 0
        if coffeeStep not in [1, 2]:
            if coffeeStep != 3:
                if (coffeeStep in [4, 5, 6]):
                    relaxStep = coffeeStep - 3
                coffeeStep = 0
        intensity = int(value[2:])
        # Explanation:
        # coffeeStep = coffee light steps (0=off, 1, 2, 3)
        # relaxStep = relax light steps (0=off, 1, 2, 3)
        # intensity = light intensity (for bio light)
        logging.info('CoffeeRelaxActivity: {:d}:{:d} / {:d}'.format(
            coffeeStep, relaxStep, intensity
        ))
        self.coffeeStep = coffeeStep
        self.relaxStep = relaxStep

    def onLatitudeReceived(self, value):
        self.latitude = float(value[1:])
        logging.info('Latitude received: {:f}'.format(self.latitude))

    def onLongitudeReceived(self, value):
        self.longitude = float(value[1:])
        logging.info('Longitude received: {:f}'.format(self.longitude))

    def onPresenceReceived(self, value):
        presActive, presSeconds = value.split(':')
        self.presenceEnabled = True if presActive == '1' else False
        self.presenceTimeout = int(presSeconds)
        logging.info('Presence received: {:s}, timeout: {:d}s'.format(
            'enabled' if self.presenceEnabled else 'disabled',
            self.presenceTimeout
        ))

    def onSunCycleTimeReceived(self, value):
        #return self.onUtcTimeReceived(value)
        pass
    
    def onUtcTimeReceived(self, value):
        """Time is provided as e.g. 20:29.06 which is in UTC"""
        utcTime = datetime.datetime.now(datetime.UTC)
        hour, minsec = value.split(':')
        minute, seconds = minsec.split('.')
        lightTime = datetime.datetime(
            utcTime.year,
            utcTime.month,
            utcTime.day,
            int(hour),
            int(minute),
            int(seconds),
            tzinfo=datetime.UTC
        )
        logging.info('Current time on light: {time}'.format(time=lightTime))
        return lightTime

    def onSunDownAndDawnReceived(self, value):
        """
        Time is given in local time if UTC offset is 
        configured correctly
        """
        dawn, down = value.split(',')
        dawnHour, dawnMinute = dawn.split(':')
        downHour, downMinute = down.split(':')
        dtDawn = datetime.datetime.now()
        self.sunDawn = dtDawn.replace(
            hour=int(dawnHour), minute=int(dawnMinute), second=0
        )
        dtDown = datetime.datetime.now()
        self.sunDown = dtDown.replace(
            hour=int(downHour), minute=int(downMinute), second=0
        )
        logging.info('Sun dawn/down received: {:s} - {:s}'.format(
            self.sunDawn.strftime('%Y-%m-%d %H:%M:%S'),
            self.sunDown.strftime('%Y-%m-%d %H:%M:%S')
        ))

    def onUtcOffsetReceived(self, value):
        self.utcOffset = int(value)
        logging.info('UTC offset received: {:d}'.format(self.utcOffset))

    def onChannelDirectReceived(self, value):
        subI8 = int(value[0:1])
        subI9 = int(value[1:])
        if subI8 == 0:
            self.onChannelTopWWReceived(subI9)
        elif subI8 == 1:
            self.onChannelTopNWReceived(subI9)
        elif subI8 == 2:
            self.onChannelTopCWReceived(subI9)
        elif subI8 == 3:
            self.onChannelMidWWReceived(subI9)
        elif subI8 == 4:
            self.onChannelMidCWReceived(subI9)
        elif subI8 == 5:
            self.onChannelMidBlueReceived(subI9)
        elif subI8 == 6:
            self.onChannelBotWWReceived(subI9)
        elif subI8 == 7:
            self.onChannelBotNWReceived(subI9)
        elif subI8 == 8:
            self.onChannelBotCWReceived(subI9)
        else:
            raise Exception('Unknown channel: {:s}'.format(str(value)))

    def onChannelTopWWReceived(self, value):
        logging.debug('Channel Top-WW: {:d}'.format(value))

    def onChannelTopNWReceived(self, value):
        logging.debug('Channel Top-NW: {:d}'.format(value))

    def onChannelTopCWReceived(self, value):
        logging.debug('Channel Top-CW: {:d}'.format(value))

    def onChannelMidWWReceived(self, value):
        logging.debug('Channel Mid-WW: {:d}'.format(value))

    def onChannelMidCWReceived(self, value):
        logging.debug('Channel Mid-CW: {:d}'.format(value))

    def onChannelMidBlueReceived(self, value):
        logging.debug('Channel Mid-Blue{:d}: '.format(value))

    def onChannelBotWWReceived(self, value):
        logging.debug('Channel Bot-WW: {:d}'.format(value))

    def onChannelBotNWReceived(self, value):
        logging.debug('Channel Bot-NW: {:d}'.format(value))

    def onChannelBotCWReceived(self, value):
        logging.debug('Channel Bot-CW: {:d}'.format(value))

    def onIntensityChanged(self, right, bio, left):
        logging.info('Intensity: {:d} / {:d} / {:d}'.format(right, bio, left))
        self.intensityLeft = left
        self.intensityBio = bio
        self.intensityRight = right
        
    def onCO2Received(self, value):
        # BME680 - it will give relative values!
        # Example: 030.46
        floatValue = float(value)
        logging.info('CO2 value read: {:.2f}'.format(floatValue))
        
    def onCO2AccuracyReceived(self, value):
        # It seems to be a BME680
        # Example: 0-3
        intVal = int(value)
        logging.info('CO2 Accuracy value read: {:d}'.format(intVal))
    
    def onAirQualityLEDReceived(self, value):
        # Example: 1
        intVal = int(value)
        logging.info('Air Quality LED value read: {:d}'.format(intVal))

    def onHumidity(self, value):
        # Example: 030.46
        floatValue = float(value)
        logging.info('Humidity read: {:.2f}'.format(floatValue))

    def onPressure(self, value):
        # Example: 097796
        intValue = int(value)
        logging.info('Pressure value read: {:d}'.format(intValue))
        
    def onTemperature(self, value):
        # Example: 030.46
        floatValue = float(value)
        logging.info('Temperature value read: {:.2f}'.format(floatValue))
        
    def onLightSensor(self, value):
        # Example: 030.46
        floatValue = float(value)
        logging.info('Light sensor value read: {:.2f}'.format(floatValue))
    
    def onManualMode(self, value):
        # Example: 0 = false, 1 = true
        intVal = int(value)
        logging.info('Manual mode value read: {:d}'.format(intVal))
    
    def onPresetData(self, value):
        # Example: 10100060
        #          ^ fix
        #           ^ side (0 = up, 1 = bio, 2 = down)
        #            ^^^ intensity
        #               ^^^ temperature
        side = int(value[1])
        sideName = self.SIDES[side]
        intensity = int(value[2:5])
        temperature = int(value[5:8])
    
        logging.info('Preset data received for {:s}: intensity = {:d}, temperature = {:d}'.format(
            sideName, intensity, temperature)
        )
