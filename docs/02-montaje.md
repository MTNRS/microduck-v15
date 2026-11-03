# Montaje de Microduck V15 R2

Sigue los IDs P01–P80 del listado. El número de cada pieza figura al principio del nombre de su STL. Consulta el despiece para orientar los lados. Los sentidos de entrada de los brazos, rodamientos y cartuchos se refieren al marco local de su motor. Los de la cabeza y el cassette se refieren a la posición de montaje del robot. Las cotas Z de pausa se miden desde la cama de impresión. [Materiales y herramientas](01-materiales.md) · [Despiece](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_modulos_separados.png) · [Sección de componentes](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_componentes_seccion.png) · [Guía ilustrada](../fabricacion/DOCUMENTACION/GUIA_IMPRESION_Y_MONTAJE_V15.html)

## 1. Probetas, pausas y pilotos

Imprime las cinco probetas con el mismo material, boquilla y altura de capa del kit. Comprueba una unidad del lote con el calibre, el brazo OEM, el conector, las tuercas y los tornillos que vas a usar. Comprueba también cómo llega el cable a la abertura del alojamiento antes de colocar una tapa. [Probetas y registro](../fabricacion/PROBETAS_PRIMERO/LEER_PRIMERO.txt) · [Registro de la primera unidad](../fabricacion/DOCUMENTACION/REGISTRO_PRIMERA_UNIDAD.csv)

Para las nueve piezas de la tabla conserva el STL en su orientación suministrada. Usa primera capa y capas siguientes de 0,20 mm, sin balsa ni altura variable. Los proyectos Prusa ya sitúan las paradas. Verifica en la vista por capas que el soporte sale sólo de la base y deja libre cada hueco de tuerca. Programa la parada según tu impresora justo después de la capa indicada. Coloca la tuerca correcta al fondo del alojamiento y verifica que queda por debajo del siguiente recorrido de la boquilla antes de reanudar.

| Piezas | Z desde la cama | Después de capa | Antes de capa | Tuercas en esa parada por pieza |
| --- | ---: | ---: | ---: | ---: |
| P14, P15, P23 | 20,0 mm | 100 | 101 | 1 |
| P04, P12 | 23,0 mm | 115 | 116 | 1 |
| P06 | 23,0 mm | 115 | 116 | 2 |
| P03 | 23,2 mm | 116 | 117 | 3 |
| P11 | 23,2 mm | 116 | 117 | 2 |
| P03, P11 | 24,2 mm | 121 | 122 | 3 |
| P44 | 45,0 mm | 225 | 226 | 4 |
| P44 | 46,0 mm | 230 | 231 | 4 |

Son 12 paradas y 26 tuercas. El CSV identifica cada tuerca por nombre y medida. Haz primero los pilotos siguientes y comprueba inserción, acceso de la llave, sujeción axial y giro libre. P01 no lleva pausa. [Pausas por tuerca](../fabricacion/PAUSAS_OBLIGATORIAS_TUERCAS_V15.csv) · [Proyectos Prusa con pausas](../fabricacion/PROYECTOS_PRUSA_PAUSAS/)

| Piloto | IDs y consumibles principales |
| --- | --- |
| Normal MG02 | P01, P14, P46, P72, P02 y P16. ET2216, brazo 14,8 mm. P14 requiere pausa. |
| Invertido MG04 | P02, P76, P03, P47 y P18. ET2216, brazo 14,8 mm. P03 requiere dos pausas. |
| MG08 | P23, P48, P07, P79 y P22. 6702ZZ y brazo 13,8 mm. P23 requiere pausa. Comprueba el casquillo impreso del eje con carga gradual. |
| Pasivo 10R | P23, P80, P69 y P30. 6701ZZ. Comprueba precarga y desmontaje antes de cerrar la cabeza. |
| Pies | Izquierdo P05, P41, P55, P56 y P59. Derecho P13, P42, P57, P58 y P60. Dos Omron SS-01-E por pie. |

Completa cada piloto con sus fijaciones del desglose por unión. La pared nominal del journal MG08 es de 0,8 mm. Verifica que conserva retención y giro tras aplicar carga progresiva en el banco. [Pilotos y orden de acoplamientos](../fabricacion/DOCUMENTACION/PILOTOS_Y_ORDEN_ACOPLAMIENTOS_V15.md) · [Tornillería por unión](../fabricacion/DOCUMENTACION/TORNILLERIA/TORNILLERIA_FUENTE_A_CONTENIDO_V15.csv)

## 2. Cuerpo delantero y acoplamientos

1. Coloca **D36 en el frontal P44 antes de MG00 y MG01**. Fija el BNO055 en sus cuatro apoyos del frontal con los M2×10 y sus arandelas y tuercas de la BOM. Conserva la orientación que muestra la sección. Deja desmontadas las tapas de entrada de servo mientras trabajas en los submódulos. Lleva los cables hacia sus pasos antes de cerrar cada tapa.
2. Monta los cinco cartuchos **00, 01, 02, 10 y 11** en el banco. Con el cartucho fuera, introduce el brazo OEM completo, con su cubo, desde +Z. Precarga las tuercas M2 por +X. En CAP00, CAP01 y CAP10 coloca arandelas y tornillos por los accesos laterales. Presenta cada tornillo 6 mm alto y bájalo por su guía. En CAP02 y CAP11, presenta ambos juegos desde +Z. Cierra el cartucho axialmente y aprieta sus dos M2.
3. Aprieta los **cinco tornillos centrales OEM** desde +Z antes de bloquear el acceso. El central 00 va antes de colocar **MG02** en CAP00. El 01 va antes de **MG11** en CAP01. El 10 va antes de **MG08** en CAP10. Aprieta los centrales 02 y 11 en el banco antes de unir sus módulos de pierna y cerrar cubiertas. Usa la punta que corresponda al tornillo del servo. Cada centro OEM se aprieta por separado de los dos M2 de tapa.
4. Carga los rodamientos de **00/01/02/03/11/12** desde +Z y monta su mitad desmontable desde el mismo lado. En **04/08/10 frontal/13**, carga el rodamiento desde −Z con la mitad desmontable, el motor y el journal opuesto fuera. Para las mitades 04 y 13 usa el acceso radial +X. Para 10 frontal, +Y. Para 08, la entrada axial −Z. Aplica la fuerza de montaje sobre el aro que recibe el ajuste.
5. Precarga los brazos **03/04/05/12/13/14** lateralmente desde +X con su CAP original colocado y las piezas que cierran la ruta fuera. Los brazos 07 y 08 se cargan desde +Z. En el 06 retira P20 y P28, instala el 623ZZ desde −Z y presenta el brazo desde +Z. Mantén acceso a sus tornillos antes de cerrar ambas tapas.
6. Prepara el pasivo **10R antes de MG08, MG10 y el brazo 10**. Precarga el M2 de P30 desde +Z en CAP10 vacío. Presenta la tuerca con P69 fuera. Instala el 6701ZZ y P80 desde +Z antes de acoplar el journal de P69. Accede con la llave AF1,5 desde −Z mientras los motores y el brazo están fuera. El tornillo se carga por el lado +Z. Respeta las dos longitudes L8 y L10 de la mejilla.
7. Monta los servos y sus cubiertas de uno en uno después de verificar los acoplamientos. Comprueba retención axial, giro, holgura y paso del cable en cada conjunto. Usa la contrallave AF4 metálica para las tuercas accesibles sin bolsillo hexagonal. El **MG09 permanece desconectado** con la mandíbula fija.

[Montaje mecánico por submódulos](../fabricacion/DOCUMENTACION/MONTAJE_POR_SUBMODULOS_V15_FINAL.md) · [Herramienta AF4](../fabricacion/DOCUMENTACION/HERRAMIENTA_AF4/LEER_CONTRALLAVE.txt)

## 3. Pies y cabeza

- **Pies.** Monta dos interruptores por pie con sus actuadores, resistencias y tapa de circuito. Comprueba por continuidad el disparo antes del tope rígido y la liberación al descargar. Las suelas y topes transmiten la carga. Engancha los ganchos de talón y los encastres de punta de cada suela. Prepara los retenes pasivos P31/P32 antes de que MG05/MG14 cierren su acceso. [Conexiones de los pies](../fabricacion/DOCUMENTACION/ARNES/ARNES_CONEXIONES_Y_TENDIDO_V15.md)
- **Cabeza.** Presenta P43 vacía. Con P69 fuera, acopla el módulo del cuello por su ruta axial y cierra la mejilla después de cargar los apoyos. Fija P43 a P37 e instala entonces la Pi Zero 2 W. Suelda los cables en los taladros GPIO de la Pi sin cabecera alta y deja accesible la microSD. Mantén el cableado fuera de los anclajes y de la salida de la cubierta superior. Ensambla cara P35, aro P40 y ojo P54 con sus fijaciones, incluidos los dos M2×10 inferiores especificados. Presenta P33 con sus cuatro cierres después de comprobar el acceso a la Pi y los cables. P39 permanece unido a la mitad inferior durante el servicio. Para retirar la cubierta, quita sus cuatro cierres, libera los cables y eleva recto en +Z. [Sección de cabeza y torso](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_componentes_seccion.png) · [Nota de servicio](../fabricacion/DOCUMENTACION/SERVICIO/NOTA_MONTAJE_SERVICIO_FINAL_V15.md)

## 4. Cassette trasero P45 en el banco

Trabaja con el pack desconectado. Prepara los pigtails y los tres soportes FR4 antes de empezar. Consulta el plano de puertos para identificar polaridad, PCM y balance.

1. **Tuercas accesibles.** Precarga las de MINI, postes inferiores ADC, clips PCM y bandejas. Reserva las cuatro tuercas y arandelas traseras PCA hasta después de cerrar los clips PCM.
2. **Control FR4.** Presenta desde +X elevado 9 mm, lleva a su posición X y baja. Coloca los dos M2×8 desde la cámara trasera antes del pack.
3. **BM, MINI y reed.** Monta el conector B3B-XH-A en su soporte FR4 con P66 y P67 antes de ADC, PCA y PDB. Sujeta MINI con sus cuatro M2×8 y el reed con P63. Aísla bornes y soldaduras.
4. **HP.** Introdúcelo desde abajo con P65 desmontado. Déjalo en sus guías hasta cerrar el panel.
5. **K10, luego PCM.** Introduce el pack preparado y aislado por abajo, con PCM y D24 fuera. Fija P61. Después sube la PCM por abajo con los clips fuera y D24 aún desmontado.
6. **ADC y clips.** Precarga las dos tuercas superiores en P64, índices 0 y 1. Presenta el soporte y ADC desde +X y coloca los cuatro M2×8. Instala después ambos clips independientes P62/P68 desde +X.
7. **D24 con P65.** Monta D24 sobre el panel inferior curvo, con sus cuatro M2×8, en el banco. Sube panel y placa juntos desde abajo después de K10 y PCM. Cierra con tres tornillos M2, dos de D24 y el de HP.
8. **PCA.** Coloca las cuatro tuercas y arandelas traseras. Prepara pigtails, R7 y pull-up de OE según el esquema. Con el PDB fuera, presenta desde +X y aprieta los cuatro M2×8. Separa los cables de su trayectoria de entrada.
9. **PDB al final.** Presenta desde +X en los dos apoyos inferiores. Fija cada uno con un M2×18, dos arandelas Ø6 × Ø2,2 × 0,5 mm y una tuerca M2. El hombro de apoyo es integral. Sujeta la placa al conectar los adaptadores.

[Orden de electrónica con accesos y fijaciones](../fabricacion/DOCUMENTACION/DAG_MONTAJE_ELECTRONICA_V15.md) · [Plano del pack y puertos](../fabricacion/DOCUMENTACION/PORT_PLAN_K10_V15.md) · [Plantillas FR4](../fabricacion/DOCUMENTACION/FR4/README_FR4_V15.md)

## 5. Conexión, cierre y primera unidad

1. Con alimentación desconectada, comprueba el arnés contra el CSV pin a pin. Revisa continuidad, polaridad, alivio de tracción y paso de los cables en juntas y articulaciones. Presenta el cassette con los conectores fuera del corredor y prepara el bucle de servicio. Conecta los cruces de arnés mientras los dos conjuntos siguen accesibles.
2. Confirma la polaridad y aparta el arnés de la junta. Desliza P45 recto hacia +X y fíjalo con sus cuatro M2×25 y arandelas de cabeza a las cuatro tuercas cautivas de P44. Para abrirlo, retira los cuatro tornillos y arandelas, desconecta y aparca el cableado cruzado y extrae el conjunto recto hacia −X. Las tuercas quedan en P44.
3. Para servicio del pack saca primero el cassette. Sigue la secuencia inversa de la pieza afectada. Retira P65 y libera la PCM antes de extraer K10, desmontando los módulos que cierren el acceso indicado en el plano. Carga el pack extraído y desconectado de ambos puertos del robot.
4. Confirma en banco el corte de protección por celda, fusible, regulación, OE y apagado por ADC antes del primer encendido con carga. La Pi recibe 5 V regulados desde D36. Mantén el canal 14 desactivado y sin conexión. Calibra cada servo en la primera unidad, comprobando sentido, neutro y extremos sin carga. Limita ambos roll de cadera a **±10° desde STAND**.

Los recorridos del kit verifican geometría nominal. Comprueba en el primer robot el lote real, la fuerza de retención, el deslizamiento, las herramientas y los cables flexibles. Las 85 poses CAD dentro del alcance son muestras del rango, con verificación de contactos a escala de 0,01 mm. El registro físico sigue pendiente hasta montar y probar la unidad. [Conexiones y corte del arnés](../fabricacion/DOCUMENTACION/ARNES/CONEXIONES_Y_CORTE_ARNES_V15.csv) · [Servicio final](../fabricacion/DOCUMENTACION/SERVICIO/NOTA_MONTAJE_SERVICIO_FINAL_V15.md) · [Calibración por servo](../fabricacion/DOCUMENTACION/CALIBRACION/CANALES_Y_CALIBRACION_UNIDADES.csv) · [Rango CAD](../fabricacion/DOCUMENTACION/CALIBRACION/HIP_ROM_LIMITES_Y_ALCANCE_V15.md) · [Registro de la primera unidad](../fabricacion/DOCUMENTACION/REGISTRO_PRIMERA_UNIDAD.csv)
