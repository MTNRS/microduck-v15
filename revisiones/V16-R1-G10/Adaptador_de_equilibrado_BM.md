# Conector del pack y salida BM

El adaptador de equilibrado recibe el XHP-3 de la batería mediante una cabecera JST B3B-XH-A en la pequeña placa FR4. Con el adaptador suelto y desconectado, la única continuidad prevista va del pin central a la isla de soldadura marcada BM. Las islas de las dos vías exteriores permanecen aisladas. El plano 1:1, el dibujo del cobre y la secuencia mecánica están en `FR4/REFERENCIA_BM`.

| Conexión | X (mm) | Y (mm) | Z (mm) | Cara |
|---|---:|---:|---:|---|
| BAT03, pin 1 | −47,45 | 20,60 | 157,35 | Entrada trasera del XHP-3 |
| BAT04, pin 2 | −47,45 | 20,60 | 159,85 | Entrada trasera del XHP-3 |
| BAT05, pin 3 | −47,45 | 20,60 | 162,35 | Entrada trasera del XHP-3 |
| W003 hacia BM del PCM | −49,00 | 32,00 | 159,85 | Isla en la cara de cobre del FR4 |

El paso de 2,50 mm discurre en Z. Hecho el corte transversal de la cabecera en Y = 32,135 mm, las tres colas de 0,64 × 0,64 mm coinciden con el plano de taladros del FR4. La vista de la página 2 de la ficha muestra cómo reconocer la marca del circuito 1 en el XHP. La página 3 especifica la cabecera B3B-XH-A de entrada superior y la separación de los terminales.

**Montaje de la revisión G8.** Suelda W003 en la isla de la cara de cobre con el adaptador y el pack separados. Las islas exteriores permanecen aisladas. Sobre la mesa, presenta la placa y la cabecera por la abertura inferior de P66, 24 mm por debajo de su asiento. Deslízalas en +Z hasta la posición final con el tramo local de W003 en la ranura. En la simulación del recorrido continuo, la placa, la cabecera y el tramo local de cable entran sin atravesar P66. En posición final, el margen nominal de las guías de FR4 es 0,10 mm; presenta la placa real y comprueba que corre sin forzar. El margen del cable durante los últimos 7 mm de colocación es de 0,485 mm. La ranura queda a 1,87 mm del tornillo de la tapa. Comprueba la continuidad de la isla central hasta W003 y su aislamiento respecto a los extremos antes de conectar ningún módulo.

La escena 09 del Blender completo muestra los dos lados de la conexión y su entrada en la tapa. El recorrido local de los cuatro conductores se ha comprobado con la cabecera, la tapa, la pieza P83 y el resto del arnés nominal. El montaje y la alimentación del robot completo siguen en ensayo.

Fuente primaria de dimensiones. JST, XH Connector, páginas 2–3. [Ficha del fabricante](https://www.jst.com/wp-content/uploads/2021/01/eXH.pdf). Hay una copia local en `Fuentes/JST_XH_especificacion.pdf`.
