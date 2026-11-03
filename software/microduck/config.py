"""Canonical V15 R2 channel map and measured calibration file format."""

from dataclasses import dataclass
import json
import math
from pathlib import Path

JOINTS = (
    ('left_hip_yaw', 0), ('left_hip_roll', 2), ('left_hip_pitch', 4),
    ('left_knee', 3), ('left_ankle', 5), ('neck_pitch', 6),
    ('head_pitch', 7), ('head_yaw', 8), ('head_roll', 10),
    ('right_hip_yaw', 1), ('right_hip_roll', 11), ('right_hip_pitch', 13),
    ('right_knee', 12), ('right_ankle', 14),
)
NAMES = tuple(name for name, _ in JOINTS)
LIMITS = {name: 10.0 if name in ('left_hip_roll', 'right_hip_roll') else 15.0 for name in NAMES}
CHECKS = ('mechanics_passed', 'harness_passed', 'oe_adc_verified', 'power_verified')
REFERENCE = 'STAND_V15_DELTA_DEG'
SCHEMA = 'microduck-v15-calibration/1'


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: número finito obligatorio')
    return float(value)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Clave duplicada: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=_unique)


def calibration_template(unit_id='', *, mock=False):
    return {
        'schema': SCHEMA, 'unit_id': unit_id, 'reference': REFERENCE,
        'mock_only': mock, 'commissioning': {k: mock for k in CHECKS},
        'axes': {
            name: {'channel': i, 'servo_index': index,
                   'servo_id': f'SIM-{index:02d}' if mock else '',
                   'points': [[-5, 1450], [0, 1500], [5, 1550]] if mock else
                             [[None, None], [0, None], [None, None]]}
            for i, (name, index) in enumerate(JOINTS)
        },
    }


@dataclass(frozen=True)
class Axis:
    channel: int
    points: tuple

    def pulse(self, angle):
        angle = number(angle, 'ángulo')
        if not self.points[0][0] <= angle <= self.points[-1][0]:
            raise ValueError(f'Canal {self.channel}: {angle:g}° fuera del intervalo medido')
        for (a0, p0), (a1, p1) in zip(self.points, self.points[1:]):
            if angle <= a1:
                return round(p0 + (p1 - p0) * (angle - a0) / (a1 - a0))
        raise AssertionError('No interval')


def validate_calibration(doc, *, real=False):
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA or doc.get('reference') != REFERENCE:
        raise ValueError('Calibración o referencia STAND desconocida')
    if not isinstance(doc.get('unit_id'), str) or not doc['unit_id'].strip():
        raise ValueError('Falta identificar la unidad')
    mock = doc.get('mock_only')
    if type(mock) is not bool or (real and mock):
        raise ValueError('La calibración sintética sólo sirve en simulación')
    checks = doc.get('commissioning')
    if not isinstance(checks, dict) or set(checks) != set(CHECKS) or any(type(v) is not bool for v in checks.values()):
        raise ValueError('Faltan las comprobaciones de primera unidad')
    if real and not all(checks.values()):
        raise ValueError('Montaje, arnés, OE/ADC y potencia deben haberse verificado en la unidad real')
    axes = doc.get('axes')
    if not isinstance(axes, dict) or set(axes) != set(NAMES):
        raise ValueError('La calibración debe contener exactamente los 14 ejes activos')
    result, servo_ids = {}, set()
    for channel, (name, index) in enumerate(JOINTS):
        row = axes[name]
        if not isinstance(row, dict) or type(row.get('channel')) is not int or type(row.get('servo_index')) is not int or (row['channel'], row['servo_index']) != (channel, index):
            raise ValueError(f'{name}: canal o servo físico incorrecto')
        servo_id = row.get('servo_id')
        if not isinstance(servo_id, str) or not servo_id.strip() or servo_id.strip() in servo_ids:
            raise ValueError(f'{name}: identifica individualmente el servo instalado')
        servo_ids.add(servo_id.strip())
        pts = row.get('points')
        if not isinstance(pts, list) or not 3 <= len(pts) <= 21 or any(not isinstance(p, list) or len(p) != 2 for p in pts):
            raise ValueError(f'{name}: se requieren pares medidos [ángulo, pulso]')
        pts = tuple((number(q, name), number(p, name)) for q, p in pts)
        angles, pulses = zip(*pts)
        if (not -LIMITS[name] <= angles[0] < 0 < angles[-1] <= LIMITS[name] or 0 not in angles or
                any(b <= a for a, b in zip(angles, angles[1:]))):
            raise ValueError(f'{name}: intervalos crecientes, cero STAND y extremos dentro de ±{LIMITS[name]:g}°')
        slopes = [b - a for a, b in zip(pulses, pulses[1:])]
        if any(not 500 <= p <= 2500 for p in pulses) or not (all(d > 0 for d in slopes) or all(d < 0 for d in slopes)):
            raise ValueError(f'{name}: pulsos medidos dentro de 500–2500 µs y monótonos en un solo sentido')
        result[name] = Axis(channel, pts)
    return result
