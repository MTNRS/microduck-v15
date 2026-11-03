# Fuentes y licencias

La [licencia de los modelos adaptados](LICENSE-MODELS.md) indica su alcance. Se incluyen para consulta sin conexión el [texto legal CC BY-NC-SA 4.0](third_party/CC-BY-NC-SA-4.0.txt) y los avisos siguientes. [modelos Pollen](third_party/POLLEN-LICENSE-MODELS.md), [Apache-2.0 de Pollen](third_party/POLLEN-APACHE-2.0.txt), [MIT del CAD de Adafruit](third_party/ADAFRUIT-CAD-MIT.txt) y [licencia de la PCB PCA9685](third_party/ADAFRUIT-PCA9685-LICENSE.txt).

## Microduck de Pollen Robotics

V15 adapta Microduck a servos MG90S y a un conjunto propio de soportes, carcasas, alimentación y cierres. La referencia geométrica se tomó de las mallas de simulación y de la descripción MJCF de `pollen-robotics/microduck_rl`, fijadas al commit `bae39f5900b318f7e87fc485c30a31213cfa14eb`. La revisión convierte la geometría a milímetros, modifica piezas y añade interfaces de montaje y servicio. [Commit de referencia](https://github.com/pollen-robotics/microduck_rl/tree/bae39f5900b318f7e87fc485c30a31213cfa14eb) · [Proyecto de Pollen Robotics](https://github.com/pollen-robotics/microduck)

- Las mallas originales de `src/mjlab_microduck/robot/microduck/assets/*.stl` son **© Pollen Robotics** y están bajo **CC BY-NC-SA 4.0**. Las adaptaciones V15 que incorporan estas mallas se distribuyen bajo **CC BY-NC-SA 4.0**. Conserva la atribución y la indicación de cambios al compartir la geometría adaptada, incluidos los STL, proyectos de impresión y CAD que la contienen. [Aviso de modelos del commit usado](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/LICENSE-MODELS.md) · [Texto legal CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
- La descripción MJCF, las configuraciones y el resto del repositorio de origen llevan **Apache-2.0**, con el alcance que declara el aviso de modelos. [Licencia Apache-2.0 del mismo commit](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/LICENSE)

## Componentes comerciales en el CAD

El montaje incluye mallas de componentes para verificar posiciones y envolventes. Cada fila distingue el archivo del fabricante o la referencia dimensional que se utilizó.

| Componente | Procedencia y tratamiento en V15 | Fuente y licencia |
| --- | --- | --- |
| goBILDA Servo Power Distribution Board `3108-2827-0801` | La BOM conserva la placa real. El CAD público representa su posición y dimensiones mediante una envolvente propia. Las auditorías históricas citaron el STEP oficial `3108-2827-0801.step` y su malla de referencia `V7_ELEC_GOBILDA_3108_2827_0801_PRIMARY_CAD`. | La edición pública excluye el STEP y su malla convertida. La ficha oficial ofrece la descarga original. [Ficha y descarga de goBILDA](https://www.gobilda.com/servo-power-distribution-board-8-channel/) |
| Adafruit ADS1115 STEMMA QT, producto 1085 | La referencia `V15_ELEC_ADS1115_1085` procede del 3MF oficial `1085 ADS1115 ADC.3mf` del commit `fc1aff4650f586f64120072ea31d5ef91efa1c42`, con transformación rígida y escala 1. El STEP se ofrece junto al 3MF en el origen. | El repositorio CAD de ese commit contiene **MIT**, © 2016 Adafruit Industries. El aviso de copyright y el texto de permiso acompañan a la redistribución del material cubierto. [Commit CAD](https://github.com/adafruit/Adafruit_CAD_Parts/commit/fc1aff4650f586f64120072ea31d5ef91efa1c42) · [Licencia MIT fijada](https://github.com/adafruit/Adafruit_CAD_Parts/blob/fc1aff4650f586f64120072ea31d5ef91efa1c42/LICENSE) |
| Adafruit PCA9685, Rev C, producto 815 | Modelo dimensional de placa y taladros a partir del EAGLE del commit `32578c83a5ba2946249b80b1aa1fb18ae4e61e7d`. El modelo refleja la configuración de montaje V15. | Los EAGLE de origen llevan **CC BY-SA 3.0 Unported**. Diseño de Limor Fried (Ladyada) para Adafruit Industries. El README de origen detalla el aviso que acompaña a una redistribución. [EAGLE Rev C y aviso del proyecto](https://github.com/adafruit/Adafruit-16-Channel-PWM-Servo-Driver-PCB/tree/32578c83a5ba2946249b80b1aa1fb18ae4e61e7d) · [Licencia fijada](https://github.com/adafruit/Adafruit-16-Channel-PWM-Servo-Driver-PCB/blob/32578c83a5ba2946249b80b1aa1fb18ae4e61e7d/license.txt) |
| Pololu D24V150F5, D36V28F5 y switch HP 2813 | Modelos dimensionales de placa y envolventes a partir de DXF y planos mecánicos. | Planos de referencia del fabricante. [DXF D24](https://www.pololu.com/file/0J1217/reg18b-drill.dxf) · [DXF D36](https://www.pololu.com/file/0J1658/reg24g-drill.dxf) · [DXF 2813](https://www.pololu.com/file/0J1099/psw03b-drill.dxf) · [Plano 2813](https://www.pololu.com/file/0J1102/big-pushbutton-power-switch-with-reverse-voltage-protection-dimension-diagram.pdf) |
| Raspberry Pi Zero 2 W | Modelo dimensional de placa, orificios y reservas de conectores. | [Plano mecánico de Raspberry Pi](https://datasheets.raspberrypi.com/rpizero2/raspberry-pi-zero-2-w-mechanical-drawing.pdf) |
| Omron SS-01-E y celdas Vapcell K10 | Referencias dimensionales locales del interruptor de pie y de las celdas. | [Ficha de Omron SS](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf) · [Ficha de Vapcell K10](https://www.vapcelltech.com/h-pd-321.html) |

El diseño EAGLE de la placa ADS1115 se consultó para sus conexiones y huellas. Su repositorio se registra por separado del repositorio que aporta el CAD 3D y su licencia MIT. [EAGLE de referencia](https://github.com/adafruit/ADS1X15-Breakout-Board-PCBs/tree/5aa7dbfdd92692a7751740b0f622606c2ff9ca55)

Las huellas SHA-256 siguientes identifican los archivos de fabricante consultados, incluido el STEP histórico de goBILDA.

| Archivo de origen | SHA-256 |
| --- | --- |
| `3108-2827-0801.step` | `8dc4744fae5e23a725c37b0475903d0544d3cfdf102e603cdf37779e3379fbd0` |
| `1085 ADS1115 ADC.3mf` | `1c8fb0b238bc21d2c411bef4ed9f06d1c1e5108b458ca61d05c4ddcefb4eac34` |

Los modelos nominales de servos, herrajes y reservas representan los componentes especificados en la documentación de montaje. El manifiesto identifica las mallas, sus huellas y los datos de procedencia disponibles. Los archivos propios separables quedan con licencia sin declarar en este inventario. Se conservan las condiciones de las fuentes correspondientes para las mallas adaptadas y los componentes de referencia incorporados. [Manifiesto del montaje](verificacion/ASSEMBLY_FABRICACION_V15.json) · [Guía de CAD](docs/06-cad.md)
