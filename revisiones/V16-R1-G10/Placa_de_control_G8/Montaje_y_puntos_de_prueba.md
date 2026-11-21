# Placa de control del Microduck

La placa sustituye la base de islas del circuito de mando. Mide 26 × 15,4 mm, con dos fijaciones M2 separadas 20 mm. Pedir FR4 de dos capas, espesor terminado 1,6 mm, cobre de 35 µm, máscara aislante en ambas caras y vías cubiertas. Los dos taladros de montaje son Ø2,20 mm sin metalizar. El archivo Gerber_control.zip contiene las capas de cobre, máscara, contorno y ambos ficheros de taladro.

## Población en banco

1. Orienta la cara de componentes como en Mapa_de_pads.svg. Los dos orificios M2 quedan cerca del borde inferior. El eje horizontal del plano crece hacia +Y del robot. El vertical crece hacia +Z. La cara de componentes mira hacia +X.
2. Suelda los siete resistores 0805. DIV_UPPER lleva 20 kΩ y DIV_LOWER 10 kΩ, ambos al 0,1 %. En BASE_PULLUP, ALERT_BASE y OE_PULLUP coloca 10 kΩ. En COLLECTOR_OFF coloca 4,7 kΩ y en OFF_PULLDOWN 100 kΩ. Las dimensiones del cobre de las huellas 0805 siguen el dibujo de reflujo de Vishay.
3. Monta Q1 onsemi 2N3906, encapsulado TO-92 de patillas rectas. Forma las tres patillas para soldarlas a las tres islas superficiales en el orden 1 emisor, 2 base y 3 colector. Contrasta la orientación de la cara plana con la vista del encapsulado de onsemi antes de doblarlas. Conserva la envolvente del encapsulado de la base anterior.
4. Con la placa sobre el banco, suelda un conductor a cada una de sus nueve islas de ramal. La tabla identifica cada hilo. Las ocho conexiones indicadas en Verificacion_independiente.json discurren por el cobre de la placa. Conserva los puntos externos del divisor, las señales y las masas protegidas que figuran en esa tabla.
5. Con la placa desconectada compara con la tabla de redes tanto la continuidad de cada pista como el aislamiento entre circuitos. Mide los dos resistores del divisor y la resistencia OFF–GND. Prueba el apagado y el arranque con una fuente de banco limitada en corriente, antes de acoplar la batería y los servos.

El análisis de los archivos de fabricación recuperó las nueve redes eléctricas a partir de los polígonos de cobre y los ocho taladros metalizados. Falta la comprobación funcional de la placa fabricada. El trazado completo del arnés, el acceso del soldador y la flexión de los hilos se evalúan por separado en el montaje del robot.

| Hilo | Isla | Destino eléctrico | Centro u/v (mm) |
|---|---|---|---|
| W025 | GND | P− protegido | 17.80 / 4.35 |
| W019 | 3V3 | Alimentación de Q1 y pullups | 7.80 / 7.85 |
| W038 | ALERT | ADS1115 ALERT/RDY | 12.30 / 13.85 |
| W045 | OE | PCA9685 OE | 9.30 / 13.85 |
| W035 | AIN0 | Entrada de medida ADS1115 AIN0 | 7.80 / 2.35 |
| W034 | VSW | Entrada del divisor desde HP.VOUT | 17.80 / 7.35 |
| W042 | OFF | Pololu 2813 OFF | 16.30 / 13.85 |

[Patillaje y encapsulado onsemi](https://www.onsemi.com/pdf/datasheet/2n3906-d.pdf) · [Dimensiones de las huellas 0805](https://www.vishay.com/docs/20035/dcrcwe3.pdf)

W037 une la isla ALERT_PI con el pin físico 11 de la Raspberry (BCM17). W044 une el pin físico 29 (BCM5) con OE_PI. W038 conserva la conexión con ALERT/RDY del ADS1115 y W045 la conexión con OE del controlador PWM. El cobre de la placa conecta los dos pares. Comprueba la continuidad de cada par y su aislamiento mutuo antes de dar tensión.
