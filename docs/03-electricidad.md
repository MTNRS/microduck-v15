# Electricidad y puesta en servicio

La V15 R2 lleva una **Raspberry Pi Zero 2 W** y 15 MG90S posicionales. Se conectan 14 motores. La mandíbula queda fija y el motor físico 09 permanece desconectado, con los canales PCA 14 y 15 deshabilitados. El CSV canónico relaciona cada canal con el índice físico de su motor. [Mapa de canales](../fabricacion/DOCUMENTACION/CALIBRACION/CANALES_Y_CALIBRACION_UNIDADES.csv) · [Conexiones, polaridades y corte del arnés](../fabricacion/DOCUMENTACION/ARNES/CONEXIONES_Y_CORTE_ARNES_V15.csv) · [Secuencia de tendido](../fabricacion/DOCUMENTACION/ARNES/ARNES_CONEXIONES_Y_TENDIDO_V15.md)

## Alimentación

El pack 2S1P usa dos Vapcell K10 y entrega B+, B− y BM a la PCM 250040. Su salida P+ pasa por el fusible MINI de 5 A y el interruptor Pololu 2813. Los dos reguladores reciben HP.VOUT. D24 proporciona 5 V al distribuidor de servos. D36 proporciona otros 5 V a la Pi y a los circuitos de pie. Todas las masas de carga vuelven a P− protegido. Mantén separados ambos positivos de 5 V y B− crudo de P−. El fusible abre la rama según su curva tiempo-corriente. [Orden de montaje](../fabricacion/DOCUMENTACION/DAG_MONTAJE_ELECTRONICA_V15.md) · [Pololu 2813](https://www.pololu.com/product/2813)

El XT30 del pack lleva B+ y B− crudos. El conector XH3 del robot sólo usa el pin central BM. Para cargar, extrae el pack y desconecta ambos conectores del robot. El plan de carga define la conexión separada de XT30 y el balanceador 2S. [Plan de puertos y carga](../fabricacion/DOCUMENTACION/PORT_PLAN_K10_V15.md)

```text
   XT30 B+ / B− ───┐
   XH3 pin 2 BM ───┴─ PCM 2S ── P+ ── MINI 5 A ── HP VIN
                            └── P− ────────────── retornos de carga
   HP VOUT ──┬── D24 IN → 5 V servos → PDB V+ → adaptadores → servos
             ├── D36 IN → 5 V lógica → Pi J8:2 y alimentación de pies
             └── 20 kΩ ── ADS AIN0 ── 10 kΩ ── P−
   Pi 3V3 ── ADS VDD, BNO VIN, PCA VCC, control Q1 y pull-up OE
   Pi SDA/SCL ── las tres placas en paralelo
   PCA S00…S13 ── señales individuales a los adaptadores (sin S del PDB)

   Q1 (2N3906): E → 3V3; B → 10 kΩ → 3V3 y 10 kΩ → ADS ALERT;
                 C → 4,7 kΩ → HP OFF; HP OFF → 100 kΩ → P−.
   ADS ALERT → Pi J8:11. Reed de encendido entre HP A y HP B.

   Por pie: D36 5 V → 2,2 kΩ → nodo S → NO talón || NO punta → P−
            S → 10 kΩ → entrada GPIO → 20 kΩ → P−. NC aislados.
```

Los tres FR4 auxiliares y las conexiones de ambos extremos están en el [directorio FR4](../fabricacion/DOCUMENTACION/FR4) y la [tabla de 118 conexiones](../fabricacion/DOCUMENTACION/ARNES/CONEXIONES_Y_CORTE_ARNES_V15.csv). Imprime las plantillas al 100 % y verifica el patrón con la pieza real antes de perforar. No uses una pista de FR4 para transportar el positivo principal entre PCM, fusible y HP.

| Pi J8 físico | BCM | Red |
| ---: | ---: | --- |
| 1 | — | 3,3 V a PCA VCC, BNO VIN, ADS VDD y control |
| 2 | — | 5 V regulados desde D36 |
| 3 | 2 | SDA a PCA 0x40, BNO 0x28 y ADS 0x48 |
| 5 | 3 | SCL del mismo bus de 3,3 V |
| 6 | — | P− protegido |
| 11 | 17 | ADS ALERT activo en bajo |
| 13 | 27 | Contacto pie derecho, activo en bajo |
| 15 | 22 | Contacto pie izquierdo, activo en bajo |
| 29 | 5 | PCA OE, nivel alto deshabilita |

Conserva los ramales V+/GND del PDB separados de las señales PWM. La señal de cada adaptador Y va a su pad de la PCA y la cavidad S del conector PDB queda vacía. Presenta los ramales reales en sus corredores, comprueba la holgura y mide el corte. [Conexiones y tendido](../fabricacion/DOCUMENTACION/ARNES/ARNES_CONEXIONES_Y_TENDIDO_V15.md)

## Bloqueo de arranque y parada

En la Adafruit 815 Rev C, retira R7 de 10 kΩ entre OE y GND y añade 10 kΩ entre OE y 3,3 V. El pull-up externo mantiene OE alto mientras el GPIO se inicializa o está liberado. El software también pone OE alto antes de abrir I²C. Configura la PCA con el prescaler 121, unos 50 Hz nominales con oscilador de 25 MHz. Inicializa los 16 canales en full-off y sólo baja OE después de verificar las salidas preparadas y las protecciones. Mide el nivel de OE y el PWM real en la primera unidad. [Adafruit 815](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts) · [PCA9685 de NXP](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)

El divisor 20 kΩ/10 kΩ toma HP.VOUT y P−. El ADS1115 arranca en 0xC293 con comparador deshabilitado. El software escribe y verifica Lo=17600 y Hi=32767, activa 0xC290, comprueba la lectura de configuración y espera 20 ms. La habilitación exige una lectura superior a 6,80 V y ALERT inactivo. El comparador usa su umbral nominal de 6,60 V y activa ALERT bajo. El 2N3906 aplica un nivel alto a HP.OFF por 4,7 kΩ. El pull-down de 100 kΩ de OFF a P− conserva el estado inactivo cuando Q1 no conduce. La PCM sigue protegiendo cada celda por separado. Verifica el corte y la retención del apagado del HP con el circuito montado. [ADS1115 de TI](https://www.ti.com/lit/ds/symlink/ads1115.pdf) · [Control y plantillas FR4](../fabricacion/DOCUMENTACION/FR4/README_FR4_V15.md)

El cierre de contexto y los fallos detectados ordenan OE alto. OE corta PWM. El HP corta las dos ramas de potencia cuando recibe la orden de apagado. En un bloqueo del sistema operativo puede quedar una salida GPIO previamente activa, por lo que la prueba de banco necesita corte de potencia accesible. El comparador autónomo empieza a actuar una vez configurado y el ensayo físico sigue pendiente.

## Diagnóstico y banco

Empieza por el comando de diagnóstico en modo simulado.

    python tools/run_robot.py doctor

En la Pi, habilita I²C y usa acceso local a /dev/i2c-1 y /dev/gpiochip0. El modo real abre smbus2 y una LGPIOFactory local explícita. Conecta el arnés de lógica y verifica el arranque con los motores desconectados. El diagnóstico real conserva OE alto, aunque programa el comparador de batería y puede provocar el apagado del HP si se alcanza su umbral.

    python tools/run_robot.py doctor --hardware

Comprueba polaridad y continuidad con el pack aislado. Mide las dos salidas de 5 V, 3,3 V, niveles de ALERT y OE, los dos divisores de pie, corte operativo y respaldo PCM. Mantén el servo piloto desacoplado y el robot apoyado durante la calibración. La capa de hardware acepta **500 a 2500 µs** y el comando de banco restringe la prueba a 1100–1900 µs durante 0,2–2,0 s. Mide y registra la ventana segura de cada unidad, incluyendo sentido, centro y topes del mecanismo. El arnés se corta después de verificar recorrido y holgura de cada articulación.

El BNO055 trabaja en IMUPLUS y entrega roll, pitch y yaw relativo en grados, además de velocidad angular x/y/z en grados por segundo. Comprueba el marco de la placa montada. La guiñada relativa deriva con el tiempo. [BNO055 de Bosch](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bno055-ds000.pdf)

Las pruebas automatizadas ejercitan los registros y GPIO con dispositivos simulados. En la primera unidad quedan por medir respuesta del corte, voltajes bajo carga, calentamiento, longitud del arnés y límites de cada servo.

## Orden de comprobación en banco

1. **Sin alimentación:** retira el pack y desconecta ambos conectores. Comprueba el arnés por redes según el CSV, incluyendo polaridad de XT30, BM en la vía 2, vías exteriores XH del robot aisladas, ausencia de cruces entre 5 V lógica y 5 V servos y ausencia de continuidad inesperada de positivos a masa. Comprueba con la placa aislada que retiraste R7 y que OE queda unido a 3,3 V sólo por el pull-up de 10 kΩ. Inspecciona aislamiento, abrazaderas y alivios.
2. **Sin Pi ni servos:** para probar sólo el lado de carga, separa la salida de la PCM y alimenta el par de entrada de carga que normalmente recibe P+/P− con una fuente de banco aislada, de polaridad comprobada y corriente limitada. Usa una tensión representativa del pack, por ejemplo 7,6 V. No conectes esta fuente al XT30 del pack, BM, B− o al pin 5 V de la Pi. Enciende HP y comprueba 5 V en la salida de cada regulador antes de conectar placas. Si una rama es incorrecta, apaga y corrige.
3. **Con Pi, sin servos:** con la fuente apagada conecta la lógica y sensores. Comprueba OE alto antes del arranque y `doctor --hardware` en la Pi. Mide 3,3 V, ambos 5 V y la relación entre HP.VOUT y ADS AIN0 (nominalmente 3:1). Mide los GPIO de pie antes de conectarlos: abierto cerca de 3,1 V, contacto cerrado cerca de 0 V. Verifica cuatro actuadores y la postura de la IMU.
4. **Corte:** con servos aún desconectados y el comparador configurado, baja lentamente la tensión de la fuente de banco. Registra el nivel al pasar por el umbral de software de 6,8 V y mide con instrumentos el nivel de ALERT y cuándo se apaga HP alrededor de 6,6 V nominal. Al subir la fuente no debe reiniciarse el HP por sí solo. Corrige cualquier fallo antes de instalar el pack. La protección por celda de la PCM se prueba por separado con un simulador de celdas y el procedimiento de su revisión; no provoques descarga profunda ni cortocircuito en celdas reales.
5. **PWM:** a tensión normal, mide con osciloscopio el canal seleccionado al ejecutar el [comando de banco](04-puesta-en-marcha.md#3-medir-cada-servo), primero sin servo. Comprueba pulso, periodo nominal de 20 ms y OE alto antes y después. Verifica que los otros canales, en particular 14 y 15, no emiten pulsos. Repite con un servo suelto y corriente limitada.
6. **Unidad completa:** desconecta la fuente de banco antes de volver a conectar la PCM y el pack. Realiza pruebas cortas con bancada, con el arnés ya asegurado y la forma final de cierre. Registra mínimos de 5 V/3,3 V, corriente pico y estable, temperatura de reguladores, celdas, conectores y cables, y el comportamiento al cortar. Conserva los límites de los componentes reales y detén la prueba ante calentamiento anormal, caída de rail, ruido, roces o disparo de protección. Usa el [registro de primera unidad](../fabricacion/DOCUMENTACION/REGISTRO_PRIMERA_UNIDAD.csv).
