# Preparar la Raspberry Pi y calibrar una unidad

Haz primero el [montaje mecánico](02-montaje.md) y el [cableado](03-electricidad.md). Usa una Raspberry Pi **Zero 2 W** con la cabecera sin pines altos. La imagen del sistema se puede descargar con [Raspberry Pi Imager](https://www.raspberrypi.com/software/); no hace falta descargar código del robot por separado.

## 1. Instalar el sistema

1. En Imager elige **Raspberry Pi Zero 2 W → Raspberry Pi OS Lite (64-bit) → microSD**. Si no tienes consola, en la personalización pon nombre de equipo `microduck`, crea tu usuario y contraseña o clave SSH, y configura Wi-Fi de **2,4 GHz** y país. Habilita SSH sólo si lo vas a usar. Comprueba qué unidad has elegido antes de escribir la imagen.
2. En el primer arranque, deja la Pi **separada del arnés del robot** si la alimentas por USB. No juntes USB y el 5 V de D36. Entra por consola o con `ssh TU_USUARIO@microduck.local` (si mDNS no funciona, usa la IP que muestra el router). No hay contraseña ni usuario predefinidos del proyecto.
3. Copia el repositorio por USB o red. Para un despliegue ligero copia `software/`, `tools/` y `examples/` manteniendo las rutas relativas. La carpeta CAD sólo hace falta en el ordenador con Blender. Por ejemplo, desde el ordenador y con SSH configurado:

   ```sh
   ssh TU_USUARIO@microduck.local "mkdir -p ~/microduck-v15"
   scp -r software tools examples TU_USUARIO@microduck.local:~/microduck-v15/
   ```

4. En la Pi, en la raíz de la copia, ejecuta `bash tools/setup_pi.sh` como tu usuario. Instala las dependencias de Raspberry Pi OS, habilita I²C y añade tu usuario a `i2c` y `gpio`. Requiere acceso al repositorio de paquetes del sistema y permisos `sudo`. No instala servicios de movimiento ni modifica el firmware de los servos. Reinicia con `sudo reboot`.

   Equivalente manual si necesitas localizar un fallo:

   ```sh
   sudo apt-get update
   sudo apt-get install python3 python3-smbus2 python3-gpiozero python3-lgpio
   sudo raspi-config nonint do_i2c 0
   sudo usermod -aG i2c,gpio "$(id -un)"
   sudo reboot
   ```

   Después: `id`, `ls -l /dev/i2c-1 /dev/gpiochip*` y `python3 -c "import smbus2, gpiozero, lgpio"`. Ejecuta el controlador como usuario normal. La referencia de opciones de Imager e I²C está en [Raspberry Pi: puesta en marcha](https://www.raspberrypi.com/documentation/computers/getting-started.html) y [configuración](https://www.raspberrypi.com/documentation/computers/configuration.html).

## 2. Diagnóstico antes de conectar servos

1. Sin alimentación, confirma polaridad, aislamiento y modificación de OE. Conecta sólo el arnés necesario para Pi, regulador lógico y sensores; deja los servos desconectados. Sigue la prueba de fuente limitada descrita en [electricidad](03-electricidad.md). El software no sustituye el multímetro, el osciloscopio ni el paro de banco.
2. Desde la raíz en la Pi ejecuta:

   ```sh
   python3 tools/run_robot.py doctor --hardware --muestras 10
   ```

   Deben responder PCA `0x40`, BNO `0x28`, ADS `0x48`. El programa verifica sus registros, informa batería y sensores, y mantiene `armed: false` y `oe_high_commanded: true`. Comprueba **en la placa** que OE está alto antes de arrancar, al salir y al desconectar el proceso. Comprueba que el voltaje coincide con la medida de `HP.VOUT` y que `alert` es `false` a tensión nominal. Pulsa talón y punta de cada pie por separado: el pie correspondiente cambia a `true`. Los ángulos del BNO se dan en el marco de la placa; verifica sentido y fijación, incluida una inclinación manual pequeña.
3. Con los servos aún desconectados, comprueba por separado el corte ADC y la respuesta del HP con una fuente de laboratorio y sin pack, siguiendo [electricidad](03-electricidad.md). El código bloquea la habilitación con tensión ≤6,8 V; el circuito físico nominal de parada es de 6,6 V. No marques el corte como comprobado si sólo observaste la cifra del programa.

## 3. Medir cada servo

Consulta el [mapa de canales y servos](../fabricacion/DOCUMENTACION/CALIBRACION/CANALES_Y_CALIBRACION_UNIDADES.csv). Marca cada servo con su índice físico y un ID único antes de conectarlo. Ejemplo: el servo físico 08 (yaw de cabeza) corresponde al canal **7**. El físico 09 y el canal 14 permanecen desconectados.

1. Con todo sin energía, conecta **un único servo**, suelto, sin carga y desacoplado del mecanismo. Coloca un brazo OEM temporal y una referencia angular. Deja libre el giro y una forma de cortar la alimentación. Ajusta la fuente al sistema de alimentación del banco; no lleves tensión del pack a los pines del servo.
2. Comienza cerca del centro, con una orden breve y observando el eje. `1500` es el primer valor de prueba, no la posición de montaje medida:

   ```sh
   python3 tools/run_robot.py banco 7 1500 --segundos 0.5 --hardware --confirmo-servo-suelto
   ```

   La orden habilita sólo ese canal durante 0,2 a 2 s, y después deshabilita la salida. Mide mientras está activo. Cambia en pasos pequeños, por ejemplo 10 µs, para medir el signo y la correspondencia de ángulos. El comando de banco restringe a 1100–1900 µs; si un servo no da un centro y margen utilizables ahí, revisa el horn y el lote antes de ampliar nada. No uses los extremos nominales para buscar topes con el motor montado.
3. Con servo desacoplado, comprueba el intervalo mecánico real y paso de cables en su módulo. Identifica la postura STAND a partir de [la vista del CAD](06-cad.md); el cero de cada eje es **su ángulo en esa postura**, no cero absoluto del servo. Coloca el horn en el estriado con el pulso de referencia ya medido y el servo desconectado de potencia durante la unión. Deja margen a ambos lados y respeta como máximo ±10° de roll de caderas y ±15° de comprobación individual en los demás. Reduce cada rango al encaje y holgura reales. No fuerces un MG90S sin alimentación para simular un eje libre.
4. Guarda un archivo por unidad:

   ```sh
   mkdir -p calibraciones-locales
   python3 tools/run_robot.py calibracion crear calibraciones-locales/V15-001.json --unidad V15-001
   ```

   En cada `axes.<nombre>` escribe el `servo_id` y al menos tres pares `points`: ángulo de junta **relativo a STAND** en grados y pulso de comando en microsegundos. Mantén las etiquetas `channel` y `servo_index`. Ordena de ángulo negativo a positivo, incluyendo `0`. Los pulsos pueden crecer o decrecer, siempre en un solo sentido. Mide los dos extremos con margen; si tienes más medidas, añade pares en orden. El pulso calculado usa el reloj nominal del PCA; comprueba con osciloscopio la frecuencia y el pulso real al habilitar un canal y conserva la misma placa al utilizar las medidas.

   Fragmento ilustrativo **para entender el formato**; no copies sus pulsos en tu unidad:

   ```json
   {"channel": 7, "servo_index": 8, "servo_id": "ETIQUETA-MG08",
    "points": [[-3, 1532], [0, 1500], [3, 1469]]}
   ```

5. Completa el [registro de primera unidad](../fabricacion/DOCUMENTACION/REGISTRO_PRIMERA_UNIDAD.csv). En el JSON pon `true` en `mechanics_passed`, `harness_passed`, `oe_adc_verified`, `power_verified` **sólo** cuando se hayan superado los ensayos correspondientes. Valida el archivo sin tocar GPIO:

   ```sh
   python3 tools/run_robot.py calibracion validar calibraciones-locales/V15-001.json --hardware
   ```

## 4. Primer movimiento con el robot sujeto

Con los 14 canales identificados, la mandíbula desconectada, el robot sujeto en una bancada y la postura STAND alineada manualmente, comprueba que puedes cortar la alimentación sin acercarte a las articulaciones. Al habilitar PWM los servos buscan su consigna inicial; su posición de arranque no se conoce por software.

```sh
python3 tools/run_robot.py ejecutar examples/01_centrado.json --calibracion calibraciones-locales/V15-001.json --hardware --confirmo-soporte --validar
python3 tools/run_robot.py ejecutar examples/01_centrado.json --calibracion calibraciones-locales/V15-001.json --hardware --confirmo-soporte
```

Revisa desviaciones, holgura, caída de tensión, consumo y temperatura antes de repetir. Si al soltar PWM la postura no se sostiene, la bancada debe mantener el robot. Usa [programación](05-programacion.md) para reducir y probar movimientos por eje; no empieces con una secuencia mayor que la calibración. Una calibración válida por formato no prueba que los números correspondan al montaje real.
