"""Protected-domain battery-voltage monitor forV15 nominal K10 architecture.

ADS1115QT1085 on0x48,3V3,AIN0=HP.VOUT/3 through20k/10k0.1%.
ALERT activeLOW drives a PNP inverter to HP2813 OFF, independently of this
process once configured. Hardware, divider and cutoff MUST be bench verified.
This file has not been deployed or tested on a physical RaspberryPi.
"""

from time import sleep

ADDRESS = 0x48
REG_CONVERSION = 0x00
REG_CONFIG = 0x01
REG_LOW = 0x02
REG_HIGH = 0x03
DIVIDER_RATIO = 3.0
ADC_LSB_V = 0.000125                 # PGA+/-4.096V, ADS1115signed16bit.
UV_CUT_V = 6.60
WARNING_V = 6.80
# OS1,MUX100(AIN0-GND),PGA001(+/-4.096),MODE0continuous,DR100128SPS,
# COMP_MODE1WINDOW,COMP_POL0activeLOW,COMP_LAT0NONLATCH,COMP_QUE00one.
CONFIG_WINDOW_UV = 0xC290
CONFIG_COMPARATOR_DISABLED = CONFIG_WINDOW_UV | 0x03
FIRST_VALID_CONVERSION_WAIT_S = 0.020  # >1/(128*0.90), TI ADS1115 RevE.
LOW_CODE = 17600                    # 6.6/3/0.000125.
HIGH_CODE = 0x7FFF                  # No normal pack voltage reaches this.


class BatteryFault(RuntimeError):
    pass


class Monitor:
    def __init__(self, bus, alert_is_low, address=ADDRESS, *, wait=sleep):
        self.bus = bus
        self.alert_is_low = alert_is_low
        self.address = address
        self._wait = wait
        self.configured = False
        self.fault_latched = False

    def _write(self, reg, value):
        self.bus.write_i2c_block_data(self.address, reg,
                                     [(value >> 8) & 255, value & 255])

    def _read(self, reg):
        value = self.bus.read_i2c_block_data(self.address, reg, 2)
        if len(value) != 2 or not all(isinstance(v, int) and 0 <= v <= 255
                                      for v in value):
            self.fault_latched = True
            raise BatteryFault("INVALID_I2C_READ")
        return (value[0] << 8) | value[1]

    def configure(self):
        """Call whilePCA9685OE is HIGH and servos remain disabled.

        POR comparator is disabled/HIGHZ, making the PNP inactive. Set both
        thresholds BEFORE enabling the window comparator. Do not use the
        default traditional comparator, which detects voltage aboveHi.
        """
        if self.fault_latched:
            raise BatteryFault("POWER_CYCLE_AND_INSPECTION_REQUIRED")
        self.configured = False
        try:
            self._write(REG_CONFIG, CONFIG_COMPARATOR_DISABLED)
            self._write(REG_LOW, LOW_CODE)
            self._write(REG_HIGH, HIGH_CODE)
            if self._read(REG_LOW) != LOW_CODE or self._read(REG_HIGH) != HIGH_CODE:
                raise BatteryFault("ADS1115_THRESHOLD_READBACK_MISMATCH")
            self._write(REG_CONFIG, CONFIG_WINDOW_UV)
            actual = self._read(REG_CONFIG)
            # OS is a status/start bit; all other config bits must read back.
            if actual & 0x7FFF != CONFIG_WINDOW_UV & 0x7FFF:
                raise BatteryFault("ADS1115_CONFIG_READBACK_MISMATCH")
            # Wait for a fresh conversion; the reset conversion register is zero.
            # Rate tolerance is +/-10%; keep OE HIGH throughout this interval.
            self._wait(FIRST_VALID_CONVERSION_WAIT_S)
            self.configured = True
        except (OSError, BatteryFault):
            self.fault_latched = True
            raise

    def sample(self):
        """Caller disables servoOE and requests halt on any fault/warning.

        WindowNONLATCH output is level-driven while voltage stays belowLo;
        conversion reads do not clear an internal comparator latch. HP itself
        latches powerOFF. CheckALERT before and after theI2Cread regardless.
        """
        if not self.configured or self.fault_latched:
            raise BatteryFault("MONITOR_NOT_ARMED_OR_PREVIOUS_FAULT")
        try:
            if self.alert_is_low():
                raise BatteryFault("HARDWARE_UV_ALERT")
            code = self._read(REG_CONVERSION)
            if code & 0x8000:
                raise BatteryFault("NEGATIVE_AIN0_OR_WIRING_ERROR")
            voltage = code * ADC_LSB_V * DIVIDER_RATIO
            if self.alert_is_low() or voltage <= UV_CUT_V:
                raise BatteryFault("OPERATING_UNDERVOLTAGE")
            if voltage > 8.60:
                raise BatteryFault("OVER_RANGE_OR_DIVIDER_FAULT")
            return {"voltage_V_nominal": voltage,
                    "warning": voltage <= WARNING_V,
                    "servo_enable_permitted_by_voltage_only": voltage > WARNING_V}
        except (OSError, BatteryFault):
            self.fault_latched = True
            raise
