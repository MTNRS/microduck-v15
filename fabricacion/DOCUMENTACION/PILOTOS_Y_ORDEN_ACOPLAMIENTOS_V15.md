# Pilotos y orden mecánico V15

La forma exterior, los 15 motores y los 14 ejes se conservan. Estas secuencias describen el espacio nominal del CAD; el ajuste del MG90S/horn OEM real, las holguras impresas y la fuerza de las uniones requieren la primera unidad. No equivalen a una validación de marcha.

## Tres pilotos antes de repetir el robot

| Piloto | Piezas impresas exactas | Interfaz que comprobar |
|---|---|---|
| Normal 02 | `V7_TAPA_BRAZO_00` (caja MG02), `V15_SERVICE_FRONT_YAW2ROLL` (mitad fija del alojamiento), `V15_ET_RADIAL_CLAMP_02F`, `V7_MOD_HIP_L`, `V7_TAPA_BRAZO_02` | ET2216 16×22×4; banda exterior de apoyo 2,45 mm; horn OEM02 de longitud total14,8 mm; pilotoOD15,6 frenteID16; CAP02 con dos M2 preparados a5,8 mm |
| Invertido04 | `V7_MOD_HIP_L`, `V15_ET_RADIAL_CLAMP_04F`, `V7_MOD_UPPER_LEG_LEFT`, `V15_SERVICE_FRONT_UPPER_LEG_LEFT_0`, `V7_TAPA_BRAZO_04` | ET2216; journalOD15,7/bore13,6; receptorOD12,8; apoyo C de unos320°; horn04 total14,8 mm; M2CAP04 originales de6 mm |
| Crítico08 | `V7_TAPA_BRAZO_10` (caja MG08), `V15_SERVICE_FRONT_YAW_ROLL_MOTION_0`, `V7_MOD_NECK_PITCH`, `V15_ET_RADIAL_CLAMP_08F`, `V7_TAPA_BRAZO_08` | **6702ZZ15×21×4**, journalOD14,7/bore13,1: pared nominal0,8 mm y holgura radial0,15 mm frente receptorOD12,8. Horn08 total13,8 mm(+0/−0,2). Alojamiento exteriorRo12,82: pared nominal2,31 mm |

Los nombres se resuelven contra el manifiesto final de ROOT, nunca contra una versión V7/R5 anterior. Cada piloto incluye el servo real, su hub/estriado OEM y tornillo central, sus dos M1,6, los dos tornillos de la tapa del horn y los dos conjuntos M2 del nuevo alojamiento. No imprimir un estriado sustituto. Los arcos del journal no deben lijarse hasta desaparecer ni forzarse contra el rodamiento.

El cierre posterior al kit limita la punta del journal08 a Z nativa +0,10001 mm y el receptor a OD12,8, manteniendo bore13,1, pared nominal0,8 y 3,7 mm de apoyo axial sobre el6702. Son los dos recortes de `CUT_TOOLS_ACTIVE08_KIT_CLEARANCE_V15.json`; no sustituirlos por geometría anterior del piloto. El alojamiento pasivo10R se orienta a41° en torno al mismo eje, con los mismos dos M2x11 y el rebaje interior complementario de LOWER. `OVERLAY_PASSIVE10_PHI41_FINAL_V15.json` y `PASSIVE10_PHI41_FINAL_PATHS_AND_ROLL_V15.json` vinculan esta revisión a sus fuentes y a31 poses sin contactos.

## Orden y ausencias deliberadas

1. Imprimir los nueve padres con las26 tuercas de la tabla final de pausas: son16 M1,6 y10 M2 ya incluidos en la BOM. Insertar en la pausa asignada; comprobar limpieza de cavidad y distancia a boquilla antes de reanudar. Los nuevos alojamientos usan tuercas postimpresión, no nuevas tuercas cerradas dentro del sólido.
2. Mantener separados los submódulos y las cubiertas de servicio. En las cajas00/01 instalar primero el módulo D36 según su secuencia de potencia. El comprobador76 incluye D36 como obstáculo en esas dos entradas.
3. Preparar los horns simétricamente: 00/01/08 a13,8 mm; 02/03/04/10/11/12/13 a14,8 mm; 05/06/07/14 a18 mm. Conservar ancho5, espesor2,4, hub y estriado de fábrica. Verificar físicamente longitud de inserción en el eje, fase y tornillo OEM antes de cerrar una caja.
4. Montar cada rodamiento en su alojamiento con la mitad desmontable y sus tornillos retirados. Los seis alojamientos normales permiten entrada axial por+MGZ; los cuatro invertidos por−MGZ. Los ensayos radiales fallidos se conservan en los informes: no usar esa ruta por conveniencia.
5. Los horns03/04/05/12/13/14 se precargan lateralmente en su receptor con la tapa OEM ya colocada y la nueva mitad del alojamiento fuera cuando cruza el recorrido. Los cinco cartuchos00/01/02/10/11 usan su carga axial/precarga OEM y sus puertos de útil comprobados. El tornillo central se aprieta antes de colocar el motor vecino que cerraría ese puerto; después se introduce ese motor por su hatch.
6. Las tuercas/arandelas del alojamiento entran desde el lado negativo de su eje de tornillo; los tornillos desde el positivo. Mantener las caras del rodamiento libres y cerrar las mitades sin usar el tornillo como prensa para corregir una desalineación. El agarre axial de estos alojamientos depende del apriete y debe superar una prueba de extracción de la primera unidad.
7. Montar los15 MG sin horn/centroscrew en la etapa de entrada indicada por76. Los servos02/08/11 van dentro de CAP00/CAP10/CAP01 respectivamente, no dentro del antiguo padre R5. Pasar el cable y conector por el puerto nominal de10×5 antes de cerrar el hatch; la posición y tamaño del cable del lote real siguen siendo una comprobación física.
8. Cabeza: cargar primero el M2 del retén pasivo10 desde+Z sobre la placa vacía y precargar la tuerca; después journal/rodamiento/cheek. El útil AF1,5 entra desde−Z con08/10 y el horn10 aún fuera. No intentar introducir el conjunto M2 completo desde−Z. La placa desmontable permite acoplar el fork sin exigir atravesar ambos journals cerrados.
9. Pasivo10: usar **6701ZZ12×18×4**, journalOD11,7 y hombro/reténOD13,6. Cargar rodamiento y mitad desmontable axialmente por+MGZ sobre CAP10 antes de instalar el cheek/journal. La retirada radial de esa mitad está bloqueada y no forma parte de la secuencia.
10. Tobillos: conservar los6700 **abiertos10×15×3**, no los ZZ de4 mm. El alivio final deja journalOD9,7,0,15 mm radial nominal y al menos2,54 mm de stock radial en torno a la tuerca M2. Precargar tuerca/retén antes de instalar el servo que taparía la cavidad.
11. Cerrar las cubiertas cosméticas al final. No usar las comprobaciones de entrada de banco como prueba de servicio con toda la electrónica y todas las carcasas ya montadas.

Para las16 tuercas sin captura hexagonal, la contrallave comprobada tiene abertura4,1 mm, cabeza de5,7 mm y grosor máximo1 mm. No hay un modelo comercial seleccionado con ese perfil: se entrega plantilla de chapa metálica SVG/DXF en `UTILES_AF4`. Desbarbar y comprobar el primer útil; no se acredita su capacidad de par. Las seis tuercas compactas08F/10F/10R usan la ranura hexagonal abierta del impreso. Los destornilladores requieren vástago de diámetro máximo3 mm y puntas AF1,5 nominal o AF1,3 para los NBK especificados.

## Aceptación de la primera unidad

El journal debe girar libre sin que hombro o retén rocen ambas pistas. Confirmar ajuste radial, captura axial, juego, acceso del útil real, ausencia de pinzamiento de cables y enganche del estriado OEM. Ensayar apriete/extracción del alojamiento y torsión del receptor/journal08 de pared0,8 mm con la carga real prevista antes de repetir piezas. No se ha medido capacidad de carga, resistencia a fatiga ni par continuo de los MG del lote.

Fuentes de forma y montaje: `OVERLAY_11_BEARING_HOUSINGS_FINAL_V15.json`, `OVERLAY_NORMAL6_CLAMPS_FROZEN_V15.json`, `OVERLAY_ACTIVE08_6702_BUILD_V15.json`, `OVERLAY_PASSIVE_6701_CLAMP_FINAL_V15.json`, `CUT_TOOLS_6700_JOURNAL_CLEARANCE_V15.json`, `ENTRADAS_HORN_CARTUCHOS_R10_METAL_Y_UTILES_V15.json`, `NECK623/OVERLAY_FLUSH_NECK_SERVICE_V15.json` y el manifiesto final de ROOT. Referencias de rodamientos: [catálogo SMB](https://www.smbbearings.com/products/thin-section-bearings.html), [6702ZZ ISK](https://iskbearing.com/product-details/6702zz), [6700 abierto3 mm SMB](https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/6700-thin-section-bearing-10x15x3mm.pdf).
