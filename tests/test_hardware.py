import struct
import os
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, patch

from microduck import hardware as h


class FakePin:
    def __init__(self, pin, events, high=None):
        self.pin = pin
        self.events = events
        self.high = high
        self.is_active = False
        self.closed = False

    def on(self):
        self.high = True
        self.events.append(("oe", True))

    def off(self):
        self.high = False
        self.events.append(("oe", False))

    def close(self):
        self.closed = True
        self.events.append(("close_gpio", self.pin, self.high))


class FakeBus:
    def __init__(self, events):
        self.events = events
        self.registers = {
            (h.BNO, 0x00): 0xA0,
            (h.BNO, 0x39): 5,
            (h.BNO, 0x3A): 0,
        }
        self.adc_words = {}
        self.bad_threshold = False
        self.fail_pwm_write = None
        self.closed = False
        self.battery(7.4)
        self.imu = list(struct.pack("<6h", 16, -32, 48, 672, -64, 80))

    def battery(self, voltage):
        self.adc_words[0] = round(voltage / 0.000375) & 0xFFFF

    def write_byte_data(self, address, register, value):
        self.events.append(("write_byte", address, register, value))
        self.registers[address, register] = value
        if address == h.PCA and 0xFA <= register <= 0xFD:
            for channel in range(16):
                self.registers[address, 0x06 + 4 * channel + register - 0xFA] = value

    def read_byte_data(self, address, register):
        self.events.append(("read_byte", address, register))
        return self.registers.get((address, register), 0)

    def write_i2c_block_data(self, address, register, values):
        self.events.append(("write_block", address, register, tuple(values)))
        if address == h.PCA and register == self.fail_pwm_write:
            raise OSError("injected I2C error")
        if address == h.ADC:
            self.adc_words[register] = int.from_bytes(values, "big")
        else:
            for offset, value in enumerate(values):
                self.write_byte_data(address, register + offset, value)

    def read_i2c_block_data(self, address, register, size):
        self.events.append(("read_block", address, register, size))
        if address == h.ADC:
            word = self.adc_words.get(register, 0)
            if register == 2 and self.bad_threshold:
                word ^= 1
            return list(word.to_bytes(2, "big"))
        if address == h.BNO and register == 0x14:
            return self.imu[:size]
        return [self.registers.get((address, register + offset), 0) for offset in range(size)]

    def close(self):
        self.closed = True
        self.events.append(("close_bus",))


class HardwareTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.pins = {}
        self.bus = FakeBus(self.events)
        self.pin_factory = Mock()
        for name, replacement in (
            ("_open_pin_factory", lambda: self.pin_factory),
            ("_open_output", self.open_output),
            ("_open_input", self.open_input),
            ("_open_bus", self.open_bus),
            ("sleep", lambda duration: self.events.append(("sleep", duration))),
        ):
            patcher = patch.object(h, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def open_output(self, pin, pin_factory):
        self.assertIs(pin_factory, self.pin_factory)
        self.events.append(("open_output_high", pin))
        device = FakePin(pin, self.events, True)
        self.pins[pin] = device
        return device

    def open_input(self, pin, pin_factory):
        self.assertIs(pin_factory, self.pin_factory)
        device = FakePin(pin, self.events)
        self.pins[pin] = device
        return device

    def open_bus(self, bus_id):
        self.events.append(("open_bus", bus_id))
        return self.bus

    def test_real_interface_boot_arm_and_exit(self):
        with h.Hardware(bus_id=7) as hw:
            self.assertEqual(self.events[:3], [("open_output_high", 5), ("oe", True), ("open_bus", 7)])
            self.assertEqual(
                [event for event in self.events if event[:3] == ("write_block", h.ADC, 1)],
                [("write_block", h.ADC, 1, (0xC2, 0x93)), ("write_block", h.ADC, 1, (0xC2, 0x90))],
            )
            running = self.events.index(("write_block", h.ADC, 1, (0xC2, 0x90)))
            self.assertLess(self.events.index(("read_block", h.ADC, 2, 2)), running)
            self.assertLess(self.events.index(("read_block", h.ADC, 3, 2)), running)
            self.assertIn(("sleep", 0.020), self.events[running:])
            self.assertEqual(self.bus.registers[h.PCA, 0xFE], 121)
            self.assertTrue(self.pins[h.OE_GPIO].high)
            with self.assertRaises(h.HardwareFault):
                hw.arm()
            hw.set_pulses({channel: 1500 for channel in range(14)})
            self.assertTrue(self.pins[h.OE_GPIO].high)
            hw.arm()
            self.assertFalse(self.pins[h.OE_GPIO].high)
            self.assertTrue(hw.status()["armed"])
            self.assertEqual(self.bus.registers[h.PCA, 0x09 + 4 * 14], 0x10)
            self.assertEqual(self.bus.registers[h.PCA, 0x09 + 4 * 15], 0x10)
            self.pins[h.FOOT_LEFT_GPIO].is_active = True
            inputs = hw.read_inputs()
            self.assertAlmostEqual(inputs["battery_v"], 7.4, places=3)
            self.assertIs(inputs["alert"], False)
            self.assertIs(inputs["foot_left"], True)
            self.assertIs(inputs["foot_right"], False)
            self.assertEqual(inputs["imu_euler_deg"], (-4, 5, 42))
            self.assertEqual(inputs["imu_gyro_dps"], (1, -2, 3))
            before = len(self.events)
            hw.status()
            self.assertEqual(len(self.events), before)
        self.assertEqual(self.events[-1], ("close_gpio", h.OE_GPIO, True))
        self.assertTrue(self.bus.closed)
        self.pin_factory.close.assert_called_once_with()
        self.assertFalse(hw.status()["armed"])
        self.assertFalse(hw.status()["open"])

    def test_bench_requires_exact_channel_and_keeps_others_off(self):
        with h.Hardware() as hw:
            hw.set_pulses({3: 1500, 4: 1500})
            with self.assertRaises(h.HardwareFault):
                hw.arm(bench_channel=3)
            hw.disarm()
            hw.set_pulses({3: 1500})
            hw.arm(bench_channel=3)
            for channel in range(16):
                if channel != 3:
                    self.assertEqual(self.bus.registers[h.PCA, 0x09 + 4 * channel], 0x10)
            hw.set_pulses({3: 1550})
            with self.assertRaises(ValueError):
                hw.set_pulses({4: 1500})
            self.assertTrue(self.pins[h.OE_GPIO].high)
            self.assertFalse(hw.status()["armed"])

    def test_arm_checks_inactive_channel_readback(self):
        with h.Hardware() as hw:
            hw.set_pulses({3: 1500})
            self.bus.registers[h.PCA, 0x09 + 4 * 14] = 0
            with self.assertRaisesRegex(h.HardwareFault, "channel 14"):
                hw.arm(bench_channel=3)
            self.assertTrue(self.pins[h.OE_GPIO].high)

    def test_bad_adc_configuration_closes_without_enabling(self):
        self.bus.bad_threshold = True
        with self.assertRaisesRegex(h.HardwareFault, "threshold"):
            with h.Hardware():
                self.fail("entered context with failed ADC readback")
        self.assertNotIn(("oe", False), self.events)
        self.assertTrue(self.pins[h.OE_GPIO].closed)
        self.assertTrue(self.bus.closed)
        self.assertNotIn(("write_block", h.ADC, 1, (0xC2, 0x90)), self.events)

    def test_alert_and_battery_voltage_disarm(self):
        with h.Hardware() as hw:
            hw.set_pulses({1: 1500})
            hw.arm(bench_channel=1)
            self.pins[h.ALERT_GPIO].is_active = True
            self.assertIs(hw.read_inputs()["alert"], True)
            self.assertTrue(self.pins[h.OE_GPIO].high)
            self.pins[h.ALERT_GPIO].is_active = False
            self.bus.battery(6.7)
            hw.set_pulses({1: 1500})
            with self.assertRaisesRegex(h.HardwareFault, "Battery"):
                hw.arm(bench_channel=1)
            self.assertFalse(hw.status()["armed"])
            self.assertEqual(hw.status()["pulses_us"], {})

    def test_runtime_pwm_write_failure_latches_fault(self):
        with h.Hardware() as hw:
            hw.set_pulses({1: 1500})
            hw.arm(bench_channel=1)
            self.bus.fail_pwm_write = 0x06 + 4
            with self.assertRaisesRegex(h.HardwareFault, "injected I2C error"):
                hw.set_pulses({1: 1600})
            self.assertTrue(self.pins[h.OE_GPIO].high)
            self.assertFalse(hw.status()["armed"])
            with self.assertRaises(h.HardwareFault):
                hw.arm(bench_channel=1)

    def test_invalid_imu_sample_is_not_replaced_by_zeros(self):
        with h.Hardware() as hw:
            hw.set_pulses({1: 1500})
            hw.arm(bench_channel=1)
            self.bus.imu = [0]
            with self.assertRaisesRegex(h.HardwareFault, "Short I2C read"):
                hw.read_inputs()
            self.assertTrue(self.pins[h.OE_GPIO].high)
            self.assertIsNone(hw.status()["last_inputs"])

    def test_same_pwm_image_skips_writes_but_rechecks_protections(self):
        with h.Hardware() as hw:
            hw.set_pulses({3: 1500})
            hw.arm(bench_channel=3)
            before = len(self.events)
            hw.set_pulses({3: 1500})
            events = self.events[before:]
            self.assertIn(("read_block", h.ADC, 0, 2), events)
            self.assertIn(("read_byte", h.PCA, 0xFE), events)
            self.assertFalse(any(event[0].startswith("write") for event in events))
            self.bus.battery(8.7)
            with self.assertRaisesRegex(h.HardwareFault, "outside valid range"):
                hw.set_pulses({3: 1500})
            self.assertTrue(self.pins[h.OE_GPIO].high)

    def test_simulation_uses_no_devices_and_validates_inputs(self):
        with h.Hardware(simulate=True) as hw:
            for mapping in ({14: 1500}, {15: 1500}, {True: 1500}, {0: True}, {0: float("nan")}, {0: 499}, {0: 2501}):
                with self.subTest(mapping=mapping), self.assertRaises(ValueError):
                    hw.set_pulses(mapping)
            hw.set_pulses({2: 500})
            hw.arm(bench_channel=2)
            hw.set_pulses({2: 2500})
            self.assertTrue(hw.status()["armed"])
            hw.disarm()
            self.assertTrue(hw.status()["oe_high_commanded"])
        self.assertEqual(self.events, [])


class LocalFactoryTests(unittest.TestCase):
    def test_real_devices_use_explicit_lgpio_even_with_mock_environment(self):
        gpiozero = ModuleType("gpiozero")
        gpiozero.DigitalOutputDevice = Mock()
        gpiozero.DigitalInputDevice = Mock()
        lgpio = ModuleType("gpiozero.pins.lgpio")
        lgpio.LGPIOFactory = Mock()
        modules = {"gpiozero": gpiozero, "gpiozero.pins.lgpio": lgpio}
        with patch.dict(sys.modules, modules), patch.dict(os.environ, {"GPIOZERO_PIN_FACTORY": "mock"}):
            pin_factory = h._open_pin_factory()
            h._open_output(5, pin_factory)
            h._open_input(17, pin_factory)
        lgpio.LGPIOFactory.assert_called_once_with(chip=0)
        gpiozero.DigitalOutputDevice.assert_called_once_with(
            5, active_high=True, initial_value=True, pin_factory=pin_factory
        )
        gpiozero.DigitalInputDevice.assert_called_once_with(
            17, pull_up=None, active_state=False, pin_factory=pin_factory
        )


if __name__ == "__main__":
    unittest.main()
