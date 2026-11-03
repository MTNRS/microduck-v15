# Materiales y preparación

Esta lista corresponde a Microduck V15 R2. El robot monta **15 MG90S posicionales de 180°**, con 14 ejes activos. El MG09 queda retenido en la cabeza, con la mandíbula fija y el canal 14 desactivado y desconectado. La placa principal es una **Raspberry Pi Zero 2 W**. El kit está verificado en CAD y laminado. Confirma las dimensiones del lote y monta los pilotos antes de imprimir el juego completo. [Guía de montaje](02-montaje.md) · [Despiece](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_modulos_separados.png)

## Piezas impresas

Imprime una unidad de cada ID del listado. Los lados izquierdo y derecho tienen sus propios STL. Las 80 piezas del robot se reparten así.

| Material | Color | Piezas |
| --- | --- | ---: |
| PETG | Negro | 60 |
| PETG | Azul cielo | 12 |
| PETG | Naranja | 2 |
| PETG | Gris | 1 |
| PETG | Amarillo | 1 |
| TPU 95A | Naranja | 2 |
| TPU 95A | Negro | 2 |

Importa los STL en milímetros a escala 100 % y conserva su orientación. El perfil verificado usa boquilla de 0,4 mm y capas de 0,20 mm, incluida la primera. Para PETG usa 4 perímetros y 40 % de relleno giroide. Para TPU usa 3 perímetros y 20 %. P45 y P65 llevan tres capas de balsa y soporte exterior. Consulta el listado para las excepciones de cada pieza. Las probetas y los dos STL de la llave magnética se preparan aparte. [STL por colores](../fabricacion/STL_POR_COLORES/) · [Listado de impresión](../fabricacion/LISTA_IMPRESION_V15.csv) · [Probetas](../fabricacion/PROBETAS_PRIMERO/LEER_PRIMERO.txt) · [Llave magnética](../fabricacion/ACCESORIOS_LLAVE/)

## Rodamientos y brazos OEM

Las dimensiones de los rodamientos se leen como diámetro interior × diámetro exterior × ancho.

| Cantidad | Referencia | Dimensiones | Uso |
| ---: | --- | --- | --- |
| 9 | ET2216 | 16 × 22 × 4 mm | Ejes principales |
| 1 | 6702ZZ | 15 × 21 × 4 mm | MG08 frontal |
| 1 | 6701ZZ | 12 × 18 × 4 mm | Apoyo pasivo 10R |
| 2 | 6700 abierto | 10 × 15 × 3 mm | Apoyos pasivos de tobillo |
| 1 | 623ZZ | 3 × 10 × 4 mm | Cuello |

El 6700 de tobillo debe ser de **3 mm de ancho**. Compra los 15 servos completos con brazos y tornillos originales. Usa el centro estriado OEM y su tornillo central. Selecciona en el lote un brazo de barra que coincida con la geometría del piloto. La referencia CAD mide 5 mm de ancho, 2,4 mm de espesor y Ø10,4 mm en el cubo. Recorta y desbarba ambos extremos por igual, conservando el cubo y el estriado.

| Motores | Cantidad de brazos | Envergadura final |
| --- | ---: | --- |
| 00, 01, 08 | 3 | 13,8 mm, +0/−0,2 mm |
| 02, 03, 04, 10, 11, 12, 13 | 7 | 14,8 mm, +0/−0,2 mm |
| 05, 06, 07, 14 | 4 | 18 mm, ±0,2 mm |

Mide con calibre el cuerpo del servo, el ancho y altura de las orejas, sus agujeros, el cubo y la salida del cable. Prueba las ventanas 02, 03 y 04 con una unidad real. La primera es de 23,4 × 12,8 mm y las siguientes añaden 0,2 y 0,4 mm a esas cotas totales. Imprime también la galga de taladros 01 y el asiento de tuercas 05. Usa los resultados para comprobar el ajuste del lote y la configuración de impresión. [BOM de electrónica y rodamientos](../fabricacion/DOCUMENTACION/BOM_ELECTRONICA_Y_RODAMIENTOS_V15.csv) · [Probetas y mediciones](../fabricacion/PROBETAS_PRIMERO/LEER_PRIMERO.txt)

## Tornillería por dimensiones

Compra por filas de la BOM. La longitud se mide bajo la cabeza. Comprueba también el diámetro y la altura de la cabeza, especialmente en los pozos de tapas y alojamientos de rodamientos.

- **179 tornillos** en total, 145 M2 y 34 M1,6, aparte de la tornillería OEM de los servos.
- **181 tuercas**, 147 M2 de 4 mm entre caras y 1,6 mm de alto, y 34 M1,6 de 3,2 mm entre caras y 1,3 mm de alto. Incluyen las 26 que se colocan durante la impresión.
- **252 arandelas**, **16 calces rígidos** y **1 casquillo metálico**. Selecciona diámetro interior, exterior y espesor según la fila. El casquillo del cuello es Ø2,98 exterior × Ø2,1 interior × 4 mm de largo.
- Dentro de ese total prepara **12 M2×6 a 5,8 mm** y **14 M2×12 a 11 mm**. Desbarba el extremo y comprueba que rosca libremente y engrana toda la altura de la tuerca.
- Conserva las referencias de cabeza baja de la BOM, incluidas NBK SSH-M2-8, SSH-M2-10 y SSHS-M2-6-SD. Las arandelas finas de los anclajes y las anchas de los dos pernos inferiores del PDB tienen dimensiones distintas.

El CSV de compra agrupa medidas y cantidades. El desglose por referencia permite comprobar qué lleva cada unión y evita contar dos veces los conjuntos de tornillo, arandela y tuerca. [Lista de compra](../fabricacion/DOCUMENTACION/TORNILLERIA/TORNILLERIA_COMPRA_V15.csv) · [Desglose por unión](../fabricacion/DOCUMENTACION/TORNILLERIA/TORNILLERIA_FUENTE_A_CONTENIDO_V15.csv)

## Electrónica

| Conjunto | Componentes de esta revisión |
| --- | --- |
| Control | Pi Zero 2 W y microSD, PCA9685 Adafruit 815 Rev C, BNO055 Adafruit 2472, ADS1115 Adafruit 1085 |
| Servos y distribución | 15 MG90S posicionales, goBILDA 3108-2827-0801, Pololu D24V150F5 #2881, Pololu D36V28F5 #3782 |
| Batería y corte | Pack 2S1P preparado con dos Vapcell K10 14500 flat-top, PCM Mantech 250040 HX-2S-D20/HY2120-CB, portafusible Littelfuse 01530007Z y fusible MINI 0297005.U de 5 A |
| Mando de alimentación | Pololu 2813, transistor 2N3906, red de resistencias del esquema, reed Littelfuse 59170-1-S-00-C e imán 57045-000 |
| Sensores de pie | Cuatro Omron SS-01-E y seis resistencias Vishay MBA0204 de 0,1 %, una de 2,2 kΩ, una de 10 kΩ y una de 20 kΩ por pie |
| Arnés y placas de soporte | Cables, terminales y conectores según el listado de corte. Soportes FR4 de MINI, BM y control según los DXF 1:1 |

Respeta el máximo de **14,7 × 52 × 29,5 mm** del cuerpo del pack, incluido aislamiento y terminales, y comprueba la salida real de los cables. Confirma la revisión recibida de la PCM y su corte por celda en banco antes de conectar el robot. Las placas deben conservar el perfil de conectores de la BOM, incluido el GPIO de bajo perfil previsto en la Pi. [BOM electrónica](../fabricacion/DOCUMENTACION/BOM_ELECTRONICA_Y_RODAMIENTOS_V15.csv) · [Conexiones y cortes](../fabricacion/DOCUMENTACION/ARNES/CONEXIONES_Y_CORTE_ARNES_V15.csv) · [Plantillas FR4](../fabricacion/DOCUMENTACION/FR4/README_FR4_V15.md) · [Pack y servicio](../fabricacion/DOCUMENTACION/PORT_PLAN_K10_V15.md)

## Herramientas de montaje

- Calibre, herramienta de desbarbado y multímetro con continuidad. Usa una punta apropiada para el tornillo central OEM.
- Llaves AF1,5 y AF1,3 para las cabezas indicadas, con vástago recto de hasta Ø3 mm en los accesos ensayados. Para los pozos de CAP00, CAP01 y CAP10 usa una llave AF1,5 acodada de hasta Ø2 mm, 15,6 mm de punta a codo y brazo de 45 mm. El CAD deja un giro de 60° en la posición de montaje indicada.
- Contrallave metálica para M2 AF4 de 1 mm de espesor y perfil de 5,7 mm, con boca de 4,1 mm. El kit incluye la plantilla a escala real. Comprueba el ajuste y la rigidez de la herramienta antes de apretar.
- Pinza para colocar tuercas en las pausas, material para retirar rebabas sin agrandar asientos, y herramientas de corte, pelado y crimpado adecuadas a los terminales del arnés.

[Plantilla y notas de la contrallave](../fabricacion/DOCUMENTACION/HERRAMIENTA_AF4/LEER_CONTRALLAVE.txt) · [Pausas y tuercas](../fabricacion/PAUSAS_OBLIGATORIAS_TUERCAS_V15.csv)
