"""Validate and play finite, supervised, open-loop V15 sequences."""

from bisect import bisect_right
from time import monotonic, sleep

from .config import NAMES, number

SCHEMA = 'microduck-v15-sequence/1'
DT = 0.05
MAX_DEG_S = 8.0
MAX_US_S = 180.0
MAX_SECONDS = 30.0


def validate_sequence(doc, axes, *, real=False):
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA:
        raise ValueError('Formato de secuencia desconocido')
    frames = doc.get('frames')
    if not isinstance(frames, list) or not 2 <= len(frames) <= 250:
        raise ValueError('Se requieren entre 2 y 250 fotogramas')
    result = []
    for index, frame in enumerate(frames):
        if not isinstance(frame, dict) or set(frame) != {'t_s', 'offset_deg'}:
            raise ValueError(f'Fotograma {index}: usa t_s y offset_deg')
        t = number(frame['t_s'], 't_s')
        offsets = frame['offset_deg']
        if not isinstance(offsets, dict) or set(offsets) - set(NAMES):
            raise ValueError('Nombre de eje desconocido o mandíbula no activa')
        q = {n: number(offsets.get(n, 0), n) for n in NAMES}
        for n in NAMES:
            axes[n].pulse(q[n])
        if not result and (t != 0 or any(q.values())):
            raise ValueError('El primer fotograma debe ser STAND (todos los desplazamientos a cero) en t=0')
        if result:
            pt, prev = result[-1]
            dt = t - pt
            if dt < DT - 1e-9 or any(abs(q[n] - prev[n]) > MAX_DEG_S * dt + 1e-9 for n in NAMES):
                raise ValueError(f'Fotograma {index}: intervalo mínimo {DT:g} s y velocidad máxima {MAX_DEG_S:g} °/s')
            if real and sum(bool(q[n] or prev[n]) for n in NAMES) > 1:
                raise ValueError('En hardware, prueba un eje por tramo y vuelve a STAND antes de cambiar de eje')
            for n in NAMES:
                lo, hi = sorted((q[n], prev[n]))
                if lo == hi:
                    continue
                for (a, p), (b, r) in zip(axes[n].points, axes[n].points[1:]):
                    if max(a, lo) < min(b, hi) and (hi - lo) / dt * abs((r - p) / (b - a)) > MAX_US_S + 1e-9:
                        raise ValueError(f'Fotograma {index}, {n}: cambio de consigna mayor de {MAX_US_S:g} µs/s')
        result.append((t, q))
    if any(result[-1][1].values()) or not 0.2 <= result[-1][0] <= MAX_SECONDS:
        raise ValueError(f'La secuencia debe acabar en STAND y durar 0.2–{MAX_SECONDS:g} s')
    return result


def interpolate(frames, time_s):
    t = max(0., min(time_s, frames[-1][0]))
    i = bisect_right([r[0] for r in frames], t) - 1
    t0, p0 = frames[i]
    if i == len(frames) - 1:
        return dict(p0)
    t1, p1 = frames[i + 1]
    f = (t - t0) / (t1 - t0)
    return {k: p0[k] + f * (p1[k] - p0[k]) for k in NAMES}


def guarded_inputs(hw, baseline=None):
    data = hw.read_inputs()
    voltage = number(data['battery_v'], 'tensión de batería')
    if data['alert'] is not False or not 6.8 < voltage <= 8.6:
        raise RuntimeError(f'Parada de alimentación: {voltage:.3f} V o ALERT activo')
    euler = tuple(number(x, 'ángulo IMU') for x in data['imu_euler_deg'])
    if len(euler) != 3:
        raise RuntimeError('Lectura IMU incompleta')
    if baseline is not None and any(abs((a - b + 180) % 360 - 180) > 20 for a, b in zip(euler[:2], baseline[:2])):
        raise RuntimeError('Parada: cambio de inclinación mayor de 20° respecto al inicio')
    return data


def play(hw, axes, frames, *, observe=lambda *_: None, clock=monotonic, wait=sleep):
    """Caller validates measured axes and full sequence before opening hardware."""
    def command(q):
        hw.set_pulses({axis.channel: axis.pulse(q[n]) for n, axis in axes.items()})

    try:
        baseline = guarded_inputs(hw)['imu_euler_deg']
        command(frames[0][1])
        hw.arm()
        t0 = clock()
        finish = frames[-1][0]
        ticks = range(1 + int(finish / DT))
        targets = [i * DT for i in ticks if i * DT < finish] + [finish]
        last_sent = t0
        last_t = 0.0
        for t in targets:
            data = guarded_inputs(hw, baseline)
            # Do not burst a backlog of servo setpoints to catch up.
            delay = max(t0 + t, last_sent + t - last_t) - clock()
            if delay > 0:
                wait(delay)
            if clock() - t0 - t > 0.2:
                raise RuntimeError('Parada: bucle atrasado más de 200 ms')
            q = interpolate(frames, t)
            last_sent, last_t = clock(), t
            command(q)
            observe(t, data, q)
    finally:
        hw.disarm()
