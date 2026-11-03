# Programar y probar la V15

El controlador está en [software/microduck](../software/microduck). Usa Python 3.10+, `smbus2` y `gpiozero` con `lgpio` para la Pi; las pruebas en ordenador usan la biblioteca estándar. En el modo por defecto no se abre el bus ni se toca GPIO. Ejecuta desde la raíz, con `python3` en la Pi:

```sh
python tools/run_robot.py --help
python tools/run_robot.py doctor
python tools/run_robot.py banco 7 1500 --segundos 0.2
python tools/run_robot.py ejecutar examples/02_cabeza.json --validar
python tools/run_robot.py ejecutar examples/02_cabeza.json --telemetria prueba-cabeza.csv
python tools/test_software.py
```

`doctor` devuelve entradas y estado local. El banco simulado termina con salidas deshabilitadas. `ejecutar` usa una calibración sintética en simulación si no pasas `--calibracion`. Ese modo prueba validación, tiempos, interpolación y telemetría; no simula dinámica, caídas, torque ni corriente. `--telemetria` crea un archivo nuevo; cambia el nombre para repetir sin sobrescribir medidas.

## Crear una secuencia

Usa el JSON de [02_cabeza.json](../examples/02_cabeza.json) como plantilla:

```json
{
  "schema": "microduck-v15-sequence/1",
  "frames": [
    {"t_s": 0, "offset_deg": {}},
    {"t_s": 0.5, "offset_deg": {"head_yaw": 2}},
    {"t_s": 1, "offset_deg": {}}
  ]
}
```

- `t_s` son segundos desde el inicio. `offset_deg` es un desplazamiento respecto de la postura STAND. Un eje omitido vale cero en ese fotograma.
- Empieza en STAND a `t=0` y termina en STAND. Usa entre 2 y 250 fotogramas, 0,2 a 30 s de duración y al menos 0,05 s entre fotogramas. Los límites son 8 °/s y 180 µs/s de cambio en la consigna PWM. El controlador interpola linealmente la posición y aplica la tabla medida para convertirla a pulsos.
- En hardware sólo se mueve un eje por tramo. Vuelve a STAND antes de cambiar de eje. Los nombres y el canal exacto están en el [CSV de canales](../fabricacion/DOCUMENTACION/CALIBRACION/CANALES_Y_CALIBRACION_UNIDADES.csv). `jaw` queda excluido. Los ángulos deben caber en la calibración real, con límite adicional de diseño de ±10° de roll en cadera y ±15° en los otros ejes de la revisión de banco.
- Valida primero en el ordenador. Para hardware usa `--hardware --calibracion calibraciones-locales/V15-001.json --confirmo-soporte --validar`. Quita `--validar` sólo con la unidad sujeta y después de la [puesta en marcha](04-puesta-en-marcha.md).

## Qué hace el controlador

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Mapa y calibración | [config.py](../software/microduck/config.py) | Canales canónicos, medidas por servo, validación y conversión interpolada. |
| Bus y GPIO | [hardware.py](../software/microduck/hardware.py) | ADS1115, PCA9685, BNO055 y pies; OE alto al arrancar, verificar, detectar fallo y cerrar. |
| Movimiento | [motion.py](../software/microduck/motion.py) | Validación completa antes de habilitar; bucle nominal de 20 Hz, límites de trayectoria y control de retraso. |
| Operación | [cli.py](../software/microduck/cli.py) | Comandos, CSV, diagnóstico, confirmación local y salida por interrupción. |

`Hardware(simulate=True)` se usa como gestor de contexto. `read_inputs()` devuelve `battery_v`, `alert`, `foot_left`, `foot_right`, `imu_euler_deg` y `imu_gyro_dps`. Las orientaciones son `(roll, pitch, yaw relativo)` y el giro `(x, y, z)` en el marco del BNO055, en grados y grados/s. No hay realimentación angular del MG90S por el cable PWM. `status()` consulta el estado interno; `oe_high_commanded` es la orden de software, no una medición del pin.

Para reutilizar el planificador desde código, mira [ejemplo Python](../examples/probar_secuencia.py). Carga la calibración con `validate_calibration`, la secuencia con `validate_sequence` y usa `play` en el contexto. Deja `real=True` en ambas validaciones si cambias el ejemplo a hardware y sigue el protocolo de banco; `set_pulses` es de bajo nivel, recibe microsegundos y su límite eléctrico no garantiza que un horn no llegue a un tope. No bajes OE directamente ni ejecutes dos programas de control a la vez.

El software corta PWM al terminar o al interrumpir (Ctrl+C o SIGTERM) y ante fallos de bus, tensión/ALERT o cambio de inclinación mayor de 20° desde el inicio. El controlador verifica el intervalo entre lecturas y manda OE alto al detectar el error. Esto no es un watchdog externo y no garantiza el corte si el sistema operativo se congela, el proceso se mata con `SIGKILL` o el cable de OE falla. El corte de subtensión del ADS→HP se comprueba aparte. Usa bancada y paro de alimentación accesible; deshabilitar el PWM deja de sostener el peso.

## Interpretar y resolver fallos

| Síntoma | Qué revisar primero |
|---|---|
| No hay `/dev/i2c-1` o permisos | Habilitar I²C, reiniciar, volver a iniciar sesión y comprobar grupo `i2c`. Ver [instalación](04-puesta-en-marcha.md). |
| Error ADS1115/ALERT | Revisar `0x48`, masa P−, configuración, divisor y voltaje real. Si HP apagó la rama, corregir causa antes de rearmar. |
| BNO055 no responde o indica fusión inválida | Confirmar VIN 3,3 V, SDA/SCL, `0x28` y masa. Revisar bus y estado de la placa antes de mover. |
| Pie activo sin pulsar o no cambia | Revisar NC/NO/COM, valores de resistencias, continuidad y nivel del GPIO sin conectar el servo. |
| PCA lee bien y servo no se mueve | Revisar con multímetro y osciloscopio el raíl 5 V de servos, OE, masa común, canal y señal directa del PCA. El PDB no lleva la señal. |
| Servo vibra, se calienta o consume demasiado | Cortar y desacoplar; revisar horn, recorrido, precarga, corriente, calibración y fuente. |
| Calibración rechazada | Identificar 14 servos distintos, aportar medidas alrededor de STAND y completar verificaciones reales. La plantilla no contiene medidas. |
| Secuencia rechazada | Reducir recorrido o aumentar los tiempos. Intercalar STAND al cambiar de eje. |
| Se corta al arrancar o al mover | Registrar voltajes con carga, revisar arnés/fusible/PCM/HP. No aumentar el fusible ni retirar el bloqueo para salvar la prueba. |

No hay realimentación de posición de los servos ni política de equilibrio o recuperación habilitada. Para desarrollar una marcha, primero mide masas y comportamiento eléctrico, valida trayectorias acopladas y vuelve a identificar el modelo de simulación con esta revisión. No reutilices una política de otro CAD o mapa de ejes en el robot real.
