"""Pi Zero 2 W I/O for the V15 wiring, with the servo gate closed by default."""
from collections.abc import Mapping
import math
from numbers import Integral, Real
import struct
from time import sleep

PCA = 0x40
BNO = 0x28
ADC = 0x48
OE_GPIO = 5
ALERT_GPIO = 17
FOOT_LEFT_GPIO = 22
FOOT_RIGHT_GPIO = 27

PWM_CLOCK_HZ = 25_000_000
PWM_HZ = 50
PRESCALE = round(PWM_CLOCK_HZ / (4096 * PWM_HZ)) - 1
ACTIVE_CHANNELS = frozenset(range(14))
MIN_PULSE_US = 500
MAX_PULSE_US = 2500
MIN_ARM_V = 6.8
MAX_VALID_PACK_V = 8.60

ADC_DISABLED = 0xC293
ADC_RUNNING = 0xC290
ADC_LO = 0x44C0
ADC_HI = 0x7FFF
FULL_OFF = (0, 0, 0, 0x10)


class HardwareFault(RuntimeError):
    """The requested operation could not be qualified with outputs disabled."""


def _open_pin_factory():
    from gpiozero.pins.lgpio import LGPIOFactory

    return LGPIOFactory(chip=0)


def _open_output(pin, pin_factory):
    from gpiozero import DigitalOutputDevice

    return DigitalOutputDevice(pin, active_high=True, initial_value=True, pin_factory=pin_factory)


def _open_input(pin, pin_factory):
    from gpiozero import DigitalInputDevice

    return DigitalInputDevice(pin, pull_up=None, active_state=False, pin_factory=pin_factory)


def _open_bus(bus_id):
    from smbus2 import SMBus

    return SMBus(bus_id)


def _pulse_bytes(pulse_us):
    ticks = round(pulse_us * PWM_CLOCK_HZ / ((PRESCALE + 1) * 1_000_000))
    return 0, 0, ticks & 0xFF, ticks >> 8


class Hardware:
    """Own one bus and the four V15 GPIOs for the duration of a context.

    Stage calibrated pulses with OE high, then arm explicitly. Calling disarm
    discards staged pulses. Use bench_channel only for one isolated servo.
    """

    def __init__(self, simulate=False, bus_id=1):
        if not isinstance(simulate, bool):
            raise TypeError("simulate must be True or False")
        self.simulate = simulate
        self.bus_id = bus_id
        self._pin_factory = None
        self._bus = None
        self._oe = None
        self._inputs = {}
        self._open = False
        self._armed = False
        self._bench_channel = None
        self._oe_high = None
        self._fault = None
        self._pulses = {}
        self._last_inputs = None

    def __enter__(self):
        if self._open:
            raise RuntimeError("Hardware context already open")
        self._fault = None
        self._last_inputs = None
        self._pulses.clear()
        try:
            if not self.simulate:
                self._pin_factory = _open_pin_factory()
                self._oe = _open_output(OE_GPIO, self._pin_factory)
            self._set_oe(True)
            if not self.simulate:
                for name, pin in (
                    ("alert", ALERT_GPIO),
                    ("foot_left", FOOT_LEFT_GPIO),
                    ("foot_right", FOOT_RIGHT_GPIO),
                ):
                    self._inputs[name] = _open_input(pin, self._pin_factory)
                self._bus = _open_bus(self.bus_id)
                self._configure_adc()
                self._configure_pca()
                self._configure_imu()
            self._open = True
            return self
        except BaseException as exc:
            self._close()
            if isinstance(exc, Exception):
                self._fault = f"Initialization failed: {exc}"
                raise HardwareFault(self._fault) from exc
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        errors = self._close()
        if errors and exc_type is None:
            raise HardwareFault("Shutdown failed: " + "; ".join(errors))
        return False

    def _set_oe(self, high):
        if self._oe is None and not self.simulate:
            self._oe_high = None
            return
        if self._oe is not None:
            try:
                if high:
                    self._oe.on()
                else:
                    self._oe.off()
            except Exception:
                self._oe_high = None
                raise
        self._oe_high = bool(high)

    def _close(self):
        errors = []
        try:
            self.disarm()
        except Exception as exc:
            errors.append(str(exc))
        # Release the output last so the board pull-up takes over.
        devices = [*self._inputs.values(), self._bus, self._oe, self._pin_factory]
        for device in devices:
            if device is not None:
                try:
                    device.close()
                except Exception as exc:
                    errors.append(str(exc))
        self._inputs.clear()
        self._bus = None
        self._oe = None
        self._pin_factory = None
        self._open = False
        if errors:
            self._fault = "Shutdown failed: " + "; ".join(errors)
        return errors

    def _require_open(self):
        if not self._open:
            raise RuntimeError("Use Hardware inside its context")

    def _check_fault(self):
        if self._fault is not None:
            raise HardwareFault(self._fault)

    def _record_fault(self, exc):
        self._fault = str(exc)
        self._armed = False
        self._bench_channel = None
        self._pulses.clear()
        try:
            self._set_oe(True)
        except Exception as oe_exc:
            self._fault += f"; could not assert OE: {oe_exc}"

    def _read_block(self, address, register, size):
        data = bytes(self._bus.read_i2c_block_data(address, register, size))
        if len(data) != size:
            raise HardwareFault(f"Short I2C read at 0x{address:02x}/0x{register:02x}")
        return data

    def _read_adc(self, register):
        return int.from_bytes(self._read_block(ADC, register, 2), "big")

    def _write_adc(self, register, value):
        self._bus.write_i2c_block_data(ADC, register, list(value.to_bytes(2, "big")))

    def _check_adc_config(self, expected=ADC_RUNNING):
        # The read value of OS is status, independent of the write value.
        if self._read_adc(1) & 0x7FFF != expected & 0x7FFF:
            raise HardwareFault("ADS1115 configuration readback mismatch")

    def _check_adc_thresholds(self):
        if self._read_adc(2) != ADC_LO or self._read_adc(3) != ADC_HI:
            raise HardwareFault("ADS1115 threshold readback mismatch")

    def _configure_adc(self):
        self._write_adc(1, ADC_DISABLED)
        self._check_adc_config(ADC_DISABLED)
        self._write_adc(2, ADC_LO)
        self._write_adc(3, ADC_HI)
        self._check_adc_thresholds()
        self._write_adc(1, ADC_RUNNING)
        self._check_adc_config()
        sleep(0.020)

    def _configure_pca(self):
        self._bus.write_byte_data(PCA, 0x00, 0x30)  # AI + SLEEP
        self._bus.write_byte_data(PCA, 0x01, 0x04)  # OUTDRV, OE high => low
        self._bus.write_byte_data(PCA, 0xFE, PRESCALE)
        self._all_off()
        self._bus.write_byte_data(PCA, 0x00, 0x20)  # Internal clock, AI
        sleep(0.001)  # Oscillator stabilization (NXP minimum 500 us)
        self._bus.write_byte_data(PCA, 0x00, 0xA0)  # RESTART + AI
        self._check_pca_config()
        self._check_pwm_image({})

    def _all_off(self):
        # Set full-off even if a reset cleared auto-increment.
        self._bus.write_byte_data(PCA, 0xFD, 0x10)
        self._bus.write_i2c_block_data(PCA, 0xFA, list(FULL_OFF))

    def _check_pca_config(self):
        mode1 = self._bus.read_byte_data(PCA, 0x00)
        mode2 = self._bus.read_byte_data(PCA, 0x01)
        prescale = self._bus.read_byte_data(PCA, 0xFE)
        if (mode1 & 0x7F, mode2 & 0x1F, prescale) != (0x20, 0x04, PRESCALE):
            raise HardwareFault("PCA9685 mode or prescaler readback mismatch")

    def _check_pwm_image(self, pulses):
        for channel in range(16):
            expected = _pulse_bytes(pulses[channel]) if channel in pulses else FULL_OFF
            actual = self._read_block(PCA, 0x06 + 4 * channel, 4)
            if actual != bytes(expected):
                raise HardwareFault(f"PCA9685 channel {channel} readback mismatch")

    def _configure_imu(self):
        # BNO055 requires time to boot, especially on a cold start.
        for _ in range(20):
            try:
                if self._bus.read_byte_data(BNO, 0x00) == 0xA0:
                    break
            except OSError:
                pass
            sleep(0.050)
        else:
            raise HardwareFault("BNO055 chip ID unavailable")
        self._bus.write_byte_data(BNO, 0x3D, 0x00)  # CONFIGMODE
        sleep(0.025)
        self._bus.write_byte_data(BNO, 0x07, 0x00)  # Page 0
        self._bus.write_byte_data(BNO, 0x3E, 0x00)  # Normal power
        self._bus.write_byte_data(BNO, 0x3B, 0x00)  # Degrees and degrees/s
        self._bus.write_byte_data(BNO, 0x3D, 0x08)  # IMUPLUS, relative heading
        for _ in range(20):
            sleep(0.050)
            if self._bus.read_byte_data(BNO, 0x39) == 5:
                self._check_imu()
                return
        raise HardwareFault("BNO055 fusion did not start")

    def _check_imu(self):
        mode = self._bus.read_byte_data(BNO, 0x3D) & 0x0F
        status, error = self._read_block(BNO, 0x39, 2)
        if mode != 8 or status != 5 or error != 0:
            raise HardwareFault("BNO055 fusion state or sensor error invalid")

    def _read_imu(self):
        self._check_imu()
        gx, gy, gz, yaw, roll, pitch = struct.unpack("<6h", self._read_block(BNO, 0x14, 12))
        angles = (roll / 16, pitch / 16, yaw / 16)
        if not (-180 <= angles[0] <= 180 and -180 <= angles[1] <= 180 and 0 <= angles[2] <= 360):
            raise HardwareFault("BNO055 Euler values outside sensor range")
        return angles, (gx / 16, gy / 16, gz / 16)

    def _read_power(self):
        if self.simulate:
            return 7.4, False
        alert_before = bool(self._inputs["alert"].is_active)
        if alert_before and self._armed:
            self.disarm()
        self._check_adc_config()
        self._check_adc_thresholds()
        count = self._read_adc(0)
        if count & 0x8000:
            count -= 0x10000
        battery = count * 0.000125 * 3
        if not 0 < battery <= MAX_VALID_PACK_V:
            raise HardwareFault("ADS1115 battery conversion outside valid range")
        return battery, alert_before or bool(self._inputs["alert"].is_active)

    def read_inputs(self):
        """Return measured inputs. Invalid data raises HardwareFault."""
        self._require_open()
        self._check_fault()
        try:
            battery, alert = self._read_power()
            if self._armed and (alert or battery <= MIN_ARM_V):
                self.disarm()
            if self.simulate:
                angles, gyro = (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
                left, right = False, False
            else:
                self._check_pca_config()
                angles, gyro = self._read_imu()
                left = bool(self._inputs["foot_left"].is_active)
                right = bool(self._inputs["foot_right"].is_active)
                alert = alert or bool(self._inputs["alert"].is_active)
                if alert and self._armed:
                    self.disarm()
            self._last_inputs = {
                "battery_v": battery,
                "alert": alert,
                "foot_left": left,
                "foot_right": right,
                "imu_euler_deg": angles,
                "imu_gyro_dps": gyro,
            }
            return dict(self._last_inputs)
        except Exception as exc:
            self._last_inputs = None
            self._record_fault(exc)
            raise HardwareFault(self._fault) from exc

    def arm(self, bench_channel=None):
        """Verify safety gates and enable either the fourteen joints or one bench channel."""
        self._require_open()
        self._check_fault()
        if self._armed:
            raise RuntimeError("Disarm before changing the enabled output set")
        if bench_channel is None:
            required = ACTIVE_CHANNELS
        else:
            if isinstance(bench_channel, bool) or not isinstance(bench_channel, Integral):
                raise ValueError("Bench channel must be an integer in 0–13")
            if bench_channel not in ACTIVE_CHANNELS:
                raise ValueError("Bench channel must be in 0–13")
            bench_channel = int(bench_channel)
            required = {bench_channel}
        if self._pulses.keys() != required:
            raise HardwareFault("Stage exactly the required channels before arming")
        inputs = self.read_inputs()
        if inputs["alert"] or inputs["battery_v"] <= MIN_ARM_V:
            self.disarm()
            raise HardwareFault("Battery or ALERT prevents arming")
        try:
            if not self.simulate:
                self._check_pwm_image(self._pulses)
                if self._inputs["alert"].is_active:
                    raise HardwareFault("ALERT asserted before enable")
            self._set_oe(False)
        except Exception as exc:
            self._record_fault(exc)
            raise HardwareFault(self._fault) from exc
        self._bench_channel = bench_channel
        self._armed = True

    def disarm(self):
        """Raise OE first, discard the pulse image, and force full-off registers."""
        self._armed = False
        self._bench_channel = None
        self._pulses.clear()
        try:
            self._set_oe(True)
        except Exception as exc:
            self._record_fault(exc)
            raise HardwareFault(self._fault) from exc
        if self._bus is not None:
            try:
                self._all_off()
            except Exception as exc:
                self._record_fault(exc)
                raise HardwareFault(self._fault) from exc

    def set_pulses(self, mapping):
        """Stage or update finite 500–2500 us pulses on permitted channels."""
        self._require_open()
        self._check_fault()
        try:
            if not isinstance(mapping, Mapping):
                raise TypeError("Pass a mapping of channel to pulse width in microseconds")
            pulses = {}
            for channel, pulse in mapping.items():
                if isinstance(channel, bool) or not isinstance(channel, Integral) or channel not in ACTIVE_CHANNELS:
                    raise ValueError("Only integer channels 0–13 are available")
                if self._bench_channel is not None and channel != self._bench_channel:
                    raise ValueError("Bench operation is restricted to its armed channel")
                if isinstance(pulse, bool) or not isinstance(pulse, Real):
                    raise ValueError("Pulse width must be a real number in microseconds")
                if not math.isfinite(pulse) or not MIN_PULSE_US <= pulse <= MAX_PULSE_US:
                    raise ValueError("Pulse width must be finite and within 500–2500 us")
                pulses[int(channel)] = float(pulse)
        except (TypeError, ValueError):
            self.disarm()
            raise
        try:
            if self._armed:
                battery, alert = self._read_power()
                if alert or battery <= MIN_ARM_V:
                    self.disarm()
                    raise HardwareFault("Battery or ALERT stopped PWM")
                if not self.simulate:
                    self._check_pca_config()
            if not self.simulate:
                for channel, pulse in pulses.items():
                    new_image = _pulse_bytes(pulse)
                    old_pulse = self._pulses.get(channel)
                    if old_pulse is not None and _pulse_bytes(old_pulse) == new_image:
                        continue
                    self._bus.write_i2c_block_data(PCA, 0x06 + 4 * channel, list(new_image))
            self._pulses.update(pulses)
        except Exception as exc:
            self._record_fault(exc)
            raise HardwareFault(self._fault) from exc

    def status(self):
        """Return local state without GPIO writes or I2C traffic."""
        return {
            "simulate": self.simulate,
            "open": self._open,
            "armed": self._armed,
            "bench_channel": self._bench_channel,
            "oe_high_commanded": self._oe_high,
            "pulses_us": dict(self._pulses),
            "pwm_hz_nominal": PWM_HZ,
            "fault": self._fault,
            "last_inputs": None if self._last_inputs is None else dict(self._last_inputs),
        }
