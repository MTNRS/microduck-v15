import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from microduck.config import JOINTS, calibration_template, read_json, validate_calibration
from microduck.hardware import Hardware
from microduck.motion import SCHEMA, interpolate, play, validate_sequence

ROOT = Path(__file__).resolve().parents[1]


def measured_fixture():
    # Synthetic measured-shaped data for exercising validators only.
    cfg = calibration_template('UNITTEST', mock=True)
    cfg['mock_only'] = False
    return cfg


def sequence(mid, t=0.5):
    return {'schema': SCHEMA, 'frames': [
        {'t_s': 0, 'offset_deg': {}},
        {'t_s': t, 'offset_deg': mid},
        {'t_s': 2*t, 'offset_deg': {}}]}


class ControlTest(unittest.TestCase):
    def test_canonical_map_matches_manufacturing(self):
        p = ROOT / 'fabricacion/DOCUMENTACION/CALIBRACION/CANALES_Y_CALIBRACION_UNIDADES.csv'
        with p.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([(r['joint'], int(r['physical_mesh_index'])) for r in rows[:14]], list(JOINTS))
        self.assertEqual([int(r['PCA9685_channel']) for r in rows], list(range(15)))
        self.assertEqual((rows[14]['joint'], rows[14]['physical_mesh_index'], rows[14]['enabled']), ('jaw', '9', 'False'))

    def test_blank_sim_and_swapped_calibration_rejected_on_hardware(self):
        for cfg in [calibration_template('PENDIENTE'), calibration_template('SIM', mock=True)]:
            with self.assertRaises(ValueError):
                validate_calibration(cfg, real=True)
        cfg = measured_fixture()
        cfg['axes']['left_hip_roll']['channel'] = 2
        with self.assertRaises(ValueError):
            validate_calibration(cfg, real=True)

    def test_reversed_servo_and_out_of_range(self):
        cfg = measured_fixture()
        cfg['axes']['head_yaw']['points'] = [[-4, 1560], [0, 1500], [4, 1470]]
        yaw = validate_calibration(cfg, real=True)['head_yaw']
        self.assertEqual((yaw.pulse(-2), yaw.pulse(2)), (1530, 1485))
        with self.assertRaises(ValueError):
            yaw.pulse(4.1)

    def test_sequence_hardware_gates(self):
        axes = validate_calibration(measured_fixture(), real=True)
        for bad in [sequence({'jaw': 1}), sequence({'left_hip_roll': 10.1}, 2),
                    sequence({'head_roll': 2}, 0.1), sequence({'head_pitch': 1, 'head_yaw': 1})]:
            with self.assertRaises(ValueError):
                validate_sequence(bad, axes, real=True)
        self.assertEqual(interpolate(validate_sequence(sequence({'head_yaw': 2}), axes), .25)['head_yaw'], 1)

    def test_steep_calibration_rejects_large_pwm_slew(self):
        cfg = measured_fixture()
        cfg['axes']['head_yaw']['points'] = [[-3, 1490], [0, 1500], [1, 1750]]
        axes = validate_calibration(cfg, real=True)
        with self.assertRaisesRegex(ValueError, 'consigna'):
            validate_sequence(sequence({'head_yaw': 1}), axes, real=True)

    def test_low_voltage_in_play_disarms(self):
        class Unstable(Hardware):
            def read_inputs(self):
                value = super().read_inputs()
                if self.status()['armed']:
                    value['battery_v'] = 6.7
                return value
        axes = validate_calibration(calibration_template('SIM', mock=True))
        frames = validate_sequence(sequence({'head_yaw': 2}), axes)
        with Unstable(simulate=True) as robot:
            with self.assertRaisesRegex(RuntimeError, 'alimentación'):
                play(robot, axes, frames)
            self.assertFalse(robot.status()['armed'])
            self.assertTrue(robot.status()['oe_high_commanded'])

    def test_cli_rejects_mock_calibration_before_opening_real_hardware(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'fake.json'
            p.write_text(json.dumps(calibration_template('SIM', mock=True)), encoding='utf-8')
            cmd = [sys.executable, '-X', 'utf8', str(ROOT/'tools/run_robot.py'), 'ejecutar',
                   str(ROOT/'examples/01_centrado.json'), '--hardware', '--confirmo-soporte', '--calibracion', str(p)]
            run = subprocess.run(cmd, capture_output=True, encoding='utf-8', timeout=10)
            self.assertEqual(run.returncode, 2)
            self.assertIn('calibración sintética', run.stderr)

    def test_json_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'duplicate.json'
            p.write_text('{"frames": [], "frames": []}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicada'):
                read_json(p)
