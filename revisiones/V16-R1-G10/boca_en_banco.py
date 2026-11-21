"""Calibración y ciclo del MG09 en una bancada independiente, PCA9685 S14."""
import argparse
import math
import time

CHANNEL = 14
HZ = 50

def ticks(pulse):
    if not 900 <= pulse <= 2100:
        raise ValueError("Pulso fuera del intervalo de trabajo de la bancada")
    return round(pulse * HZ * 65535 / 1_000_000)

def cycle(closed, opened):
    if not 20 <= abs(opened - closed) <= 400:
        raise ValueError("Comprueba los pulsos medidos a 0 y 22 grados")
    ticks(closed)
    ticks(opened)
    steps = math.ceil(abs(opened - closed) / 4)
    for i in range(steps + 1):
        yield round(closed + (opened - closed) * i / steps)
    for i in range(1, steps + 1):
        yield round(opened + (closed - opened) * i / steps)

def jog(send):
    pulse = 1500
    send(pulse)
    print("1500 µs. Alinea el brazo. Usa + o - para avanzar 5 µs, q para soltar.")
    while True:
        key = input(f"{pulse} µs > ").strip()
        if key == "q":
            return
        if key not in {"+", "-"}:
            continue
        new = pulse + (5 if key == "+" else -5)
        if 900 <= new <= 2100:
            send(new)
            pulse = new

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibrar", action="store_true")
    parser.add_argument("--cerrado-us", type=int)
    parser.add_argument("--abierto-us", type=int)
    parser.add_argument("--activar-banco", action="store_true", help="Emite PWM por S14 en un PCA9685 dedicado al MG09")
    args = parser.parse_args()
    pulses = []
    if not args.calibrar:
        if args.cerrado_us is None or args.abierto_us is None:
            parser.error("Indica los dos pulsos medidos o utiliza --calibrar")
        try:
            pulses = list(cycle(args.cerrado_us, args.abierto_us))
        except ValueError as exc:
            parser.error(str(exc))
    elif args.cerrado_us is not None or args.abierto_us is not None:
        parser.error("Para calibrar se ajusta un pulso cada vez")
    if not args.activar_banco:
        print(f"Ensayo sin hardware. Canal S{CHANNEL:02}, {HZ} Hz.")
        if pulses:
            print(f"{len(pulses)} consignas: {pulses[0]} → {args.abierto_us} → {pulses[-1]} µs")
        return
    import board
    from adafruit_pca9685 import PCA9685
    i2c = board.I2C()
    pca = None
    try:
        pca = PCA9685(i2c, address=0x40)
        ch = pca.channels[CHANNEL]
        ch.duty_cycle = 0
        pca.frequency = HZ
        def send(pulse):
            ch.duty_cycle = ticks(pulse)
        if args.calibrar:
            jog(send)
        else:
            for pulse in pulses:
                send(pulse)
                time.sleep(0.04)
    finally:
        try:
            if pca is not None:
                try:
                    pca.channels[CHANNEL].duty_cycle = 0
                finally:
                    pca.deinit()
        finally:
            i2c.deinit()

if __name__ == "__main__":
    main()

