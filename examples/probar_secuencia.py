"""Exercise the same controller without physical outputs."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'software'))
from microduck.config import calibration_template, read_json, validate_calibration
from microduck.hardware import Hardware
from microduck.motion import play, validate_sequence


def main():
    axes = validate_calibration(calibration_template('SIMULACION', mock=True))
    sequence = validate_sequence(read_json(ROOT / 'examples' / '02_cabeza.json'), axes)
    with Hardware(simulate=True) as robot:
        play(robot, axes, sequence,
             observe=lambda t, data, q: print(f'{t:4.2f} s, {data["battery_v"]:.2f} V, yaw={q["head_yaw"]:+.2f}°'))
        print(f'Salidas habilitadas al finalizar: {robot.status()["armed"]}')


if __name__ == '__main__':
    main()
