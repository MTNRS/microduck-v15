"""Command-line commissioning: no outputs without explicit hardware and consent."""

import argparse
import csv
from contextlib import nullcontext
import json
from pathlib import Path
import signal
import sys
from time import monotonic, sleep

from .config import JOINTS, NAMES, calibration_template, read_json, validate_calibration
from .hardware import Hardware
from .motion import DT, guarded_inputs, play, validate_sequence


def emit(value):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)


def _device(args):
    return Hardware(simulate=not args.hardware, bus_id=args.bus)


def diagnostics(args):
    if not 1 <= args.muestras <= 100:
        raise ValueError('Usa 1–100 muestras')
    with _device(args) as hw:
        for i in range(args.muestras):
            emit({'modo': 'hardware' if args.hardware else 'simulación', 'entrada': hw.read_inputs(),
                  'estado': hw.status()})
            if i + 1 < args.muestras:
                sleep(0.2)


def create_cal(args):
    if not args.unidad.strip():
        raise ValueError('Identifica la unidad, por ejemplo V15-001')
    with Path(args.archivo).open('x', encoding='utf-8') as out:
        json.dump(calibration_template(args.unidad), out, indent=2, ensure_ascii=False)
        out.write('\n')
    emit({'plantilla': str(args.archivo), 'mediciones_pendientes': True})


def check_cal(args):
    cal = read_json(args.archivo)
    axes = validate_calibration(cal, real=args.hardware)
    emit({'unidad': cal['unit_id'], 'ejes': len(axes), 'archivo_valido': True,
          'tipo': 'sintético' if cal['mock_only'] else 'mediciones de usuario', 'salidas_activadas': False})


def bench(args):
    if not 0 <= args.canal <= 13 or not 1100 <= args.pulso_us <= 1900 or not 0.2 <= args.segundos <= 2.0:
        raise ValueError('Banco: canal 0–13, pulso 1100–1900 µs y duración 0.2–2.0 s')
    if args.hardware and not args.confirmo_servo_suelto:
        raise ValueError('En banco sólo un servo suelto. Confirma con --confirmo-servo-suelto')
    with _device(args) as hw:
        try:
            guarded_inputs(hw)
            hw.set_pulses({args.canal: args.pulso_us})
            hw.arm(bench_channel=args.canal)
            deadline = monotonic() + args.segundos
            while monotonic() < deadline:
                guarded_inputs(hw)
                sleep(max(0, min(DT, deadline - monotonic())))
        finally:
            hw.disarm()
    emit({'canal': args.canal, 'servo_físico': JOINTS[args.canal][1], 'pulso_us': args.pulso_us,
          'hardware': args.hardware, 'salidas_desactivadas': True})


def run(args):
    if args.hardware and (not args.confirmo_soporte or args.calibracion is None):
        raise ValueError('Hardware requiere calibración medida y --confirmo-soporte')
    cal = read_json(args.calibracion) if args.calibracion else calibration_template('SIMULACION', mock=True)
    axes = validate_calibration(cal, real=args.hardware)
    frames = validate_sequence(read_json(args.secuencia), axes, real=args.hardware)
    if args.validar:
        emit({'unidad': cal['unit_id'], 'fotogramas': len(frames), 'duración_s': frames[-1][0],
              'validada': True, 'salidas_activadas': False})
        return
    with (Path(args.telemetria).open('x', encoding='utf-8', newline='') if args.telemetria else nullcontext()) as stream:
        writer = csv.writer(stream) if stream else None
        if writer:
            writer.writerow(['t_s', 'battery_v', 'alert', 'foot_left', 'foot_right', 'imu_roll', 'imu_pitch',
                             'imu_yaw_rel', 'gyro_x', 'gyro_y', 'gyro_z', *NAMES])
        def record(t, data, q):
            if writer:
                writer.writerow([round(t, 5), data['battery_v'], data['alert'], data['foot_left'], data['foot_right'],
                                 *data['imu_euler_deg'], *data['imu_gyro_dps'], *(round(q[n], 5) for n in NAMES)])
        with _device(args) as hw:
            play(hw, axes, frames, observe=record)
    emit({'unidad': cal['unit_id'], 'duración_s': frames[-1][0], 'hardware': args.hardware,
          'salidas_desactivadas': True, 'telemetría': args.telemetria})


def _device_args(parser):
    parser.add_argument('--hardware', action='store_true', help='acceder a la Pi real; por defecto simula')
    parser.add_argument('--bus', type=int, default=1, choices=[1], help='bus I²C de J8 (1)')


def parser():
    p = argparse.ArgumentParser(description='Microduck V15 R2: diagnóstico, calibración y secuencias de banco')
    sub = p.add_subparsers(dest='comando', required=True)
    doc = sub.add_parser('doctor', help='lee sensores, sin habilitar PWM')
    _device_args(doc)
    doc.add_argument('--muestras', type=int, default=1)
    doc.set_defaults(call=diagnostics)
    cal = sub.add_parser('calibracion', help='crear plantilla bloqueada o validar un archivo')
    mode = cal.add_subparsers(dest='accion', required=True)
    create = mode.add_parser('crear')
    create.add_argument('archivo', type=Path)
    create.add_argument('--unidad', required=True)
    create.set_defaults(call=create_cal)
    check = mode.add_parser('validar')
    check.add_argument('archivo', type=Path)
    check.add_argument('--hardware', action='store_true', help='aplicar requisitos reales; nunca accede a GPIO')
    check.set_defaults(call=check_cal)
    ben = sub.add_parser('banco', help='pulso acotado en un solo servo desacoplado')
    _device_args(ben)
    ben.add_argument('canal', type=int)
    ben.add_argument('pulso_us', type=int)
    ben.add_argument('--segundos', type=float, default=0.5)
    ben.add_argument('--confirmo-servo-suelto', action='store_true')
    ben.set_defaults(call=bench)
    exe = sub.add_parser('ejecutar', help='validar o ejecutar una secuencia finita')
    _device_args(exe)
    exe.add_argument('secuencia', type=Path)
    exe.add_argument('--calibracion', type=Path)
    exe.add_argument('--telemetria')
    exe.add_argument('--confirmo-soporte', action='store_true')
    exe.add_argument('--validar', action='store_true', help='sólo valida, sin abrir GPIO ni bus')
    exe.set_defaults(call=run)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    def interrupt(_sig, _frame):
        raise KeyboardInterrupt
    original = signal.signal(signal.SIGTERM, interrupt)
    try:
        args.call(args)
        return 0
    except KeyboardInterrupt:
        print('Interrumpido; se ha solicitado desactivar las salidas.', file=sys.stderr)
        return 130
    except (OSError, ValueError, RuntimeError, ImportError, KeyError, TypeError, OverflowError) as exc:
        print(f'Microduck: {exc}', file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, original)
