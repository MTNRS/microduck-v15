# Plantillas FR4 V15

Tres bases **FR4 de1.6 mm**, coherentes con los modelos3D activos. Cada una tiene SVG a1:1, DXF en milímetros y CSV de centros. Los4.728 rayos de comprobación de contorno y taladros contra los NPZ dieron **0 discrepancias**; el recibo con hashes está en `FR4_MANIFEST.json`. No se ha comprobado una impresora ni una placa física.

| Base | Medida exterior | Taladros |
|---|---|---|
| BM/JST |8×9.8 mm, muesca0.7×1.6 |3×Ø1.0, paso2.5 |
| MINI |30.3×20.5 mm, recorte superior11.72×5.933 |2×Ø1.27 eléctricos,1×Ø2.0828 boardlock,4×Ø2.2 M2 |
| Control |26×15.4 mm |2×Ø2.2 M2 |

Imprimir los SVG **al100%, sin «ajustar a página»**. Comprobar primero la regla100 mm y el cuadrado10×10; si no coinciden, no usar el papel para marcar. DXF declara unidades mm. En todos los planos, **u crece hacia la derecha y v hacia arriba**, desde la esquina inferior izquierda. La línea negra es corte, los círculos azules son taladros y los contornos grises sólo indican componentes. No taladrar los contornos grises ni los centros de resistores.

Recortar, desbarbar y probar las bases vacías en sus alojamientos antes de soldar. Las dimensiones de orificio son las nominales del modelo; comprobar el ajuste del boardlock con la pieza suministrada, sin forzar ni agrietar el FR4. No modificar ni taladrar las PCB compradas de Adafruit, Pololu o goBILDA con estas plantillas.

## BM: central exclusivamente

La plantilla mecánica se ve por la **cara de componentes−Y**. La guía de cobre posterior se ve por **+Y y está espejada**; no mezclar ambas vistas. La muesca queda a la izquierda en la vista de componentes y a la derecha en la posterior.

| Pin del dibujo | u/v en vista componentes, mm | Conexión en el robot |
|---|---|---|
|1 inferior |3.475 /2.45 |NC, isla independiente y aislada |
|2 central |3.475 /4.95 |Únicamente PCM.BM |
|3 superior |3.475 /7.45 |NC, isla independiente y aislada |

La guía posterior conserva los islotes OD2 mm y el enlace central de0.6 mm al pad BM OD1.6. No es un Gerber ni se supone una pista de potencia. Puede montarse con el islote central y un pigtail aislado, manteniendo los dos laterales desconectados e individualmente aislados. **No puentear B− crudo con P− protegido**: el robot sólo toma el pin central de esta pareja XH.

Montar B3B-XH-A, soldar y recortar **únicamente las colas de soldadura** a2.4 mm totales desde la cara frontal del FR4: quedan0.8 mm por detrás de la base1.6. No recortar contactos de acoplamiento ni carcasa. Repasar extremos y aislar; comprobar con continuidad que pin2 llega a BM y que1/3 siguen abiertos. La retención y secuencia son las del overlay BM final; la plantilla no cambia su pose.

## MINI: terminales directos

La vista es desde el portafusible, por **−Y**. Los orificios PWR_IN/PWR_OUT corresponden a los terminales del01530007Z; el central grande es su boardlock, no una conexión eléctrica. El fusible es no polar: los nombres IN/OUT fijan el arnés del robot, no una polaridad interna del fusible.

`PCM.P+ → terminal IN → MINI5A → terminal OUT → HP.VIN`

Soldar el cable aislado16AWG directamente a los terminales. **La corriente no circula por una pista FR4 cuya capacidad se haya supuesto.** El soporte conserva las patillas completas de su modelo; aislar ambos bornes por separado y dar alivio a los cables para que no arranquen las soldaduras al extraer un conector. Mantener metal expuesto y rebabas lejos de arandelas, tornillos y envoltura del pack. La coordinación del fusible y el ensayo bajo carga siguen siendo pruebas del primer conjunto.

## Control: colocación y conexiones

Vista desde la cara de componentes **+X**. Los dos taladros sólo fijan la base; los elementos0805 y las patillas formadas se montan en **islotes/cableado manual aislado**. No se entrega una PCB ruteada ni se han inventado taladros para el paso de patillas TO92. La zona Q1 del dibujo es una asignación de6×6 mm, no una huella de taladro del fabricante.

| Elemento | Centro u/v, mm | Valor | Conexión |
|---|---|---|---|
|DIV_UPPER |10.5 /1.7 |20k,0.1% |HP.VOUT → ADS.AIN0 |
|DIV_LOWER |14.5 /1.7 |10k,0.1% |ADS.AIN0 → P− |
|BASE_PULLUP |18.5 /1.7 |10k |Pi3V3 → Q1 base |
|ALERT_BASE |10.5 /11.7 |10k |ADS.ALERT → Q1 base |
|COLLECTOR_OFF |14.5 /11.7 |4.7k |Q1 colector → HP.OFF |
|OFF_PULLDOWN |18.5 /11.7 |100k |HP.OFF → P− |
|PCA_OE_PULLUP |6.5 /10.2 |10k |Pi3V3 → PCA.OE |
|Q1 |12.5 /6.2 |onsemi2N3906 |Emisor→Pi3V3; base y colector según filas anteriores |

Confirmar el patillaje del2N3906 suministrado con su ficha antes de formar y aislar las patillas. No utilizar el soporte mecánico como mapa universal para otro transistor. Sujetar los componentes y usar conexiones cortas aisladas; comprobar cada red y la ausencia de puentes antes de conectar el pack. El plano no acredita el recorrido completo de esos puentes ni el ensayo eléctrico.

**El resistor externo PCA_OE_PULLUP no es PCA.R7.** Retirar PCA.R7 de10k aGND de la Adafruit815 RevC y colocar el pullup externo indicado. OE queda en **BCM5/pin físico29**; ALERT en **BCM17/pin11**. Los pies conservan22/27 y su PN final es **Omron SS-01-E**. Todas las masas de esta base son P− protegido, nunca B− crudo.

El divisor toma **HP.VOUT conmutada**, no P+ permanentemente vivo. El ADS se alimenta a3.3V. El código activo de `ADC_SOFTWARE` deshabilita primero el comparador, verifica umbrales y espera conversión válida antes de habilitarlo. La placa Adafruit comprada conserva sus taladros y geometría; no se fabrica a partir de este plano.

Los esquemas nominales y fuentes verificadas se conservan en `ADC_OPERATING_STOP_V15.json`, `PCA_OE_BOOT_REWORK_V15.json`, el overlay BM final y las fichas archivadas de [Littelfuse153](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-mini-153-pc-datasheet.pdf?assetguid=3c98b789-a8a0-4bb5-aac4-61f242a65615) y [onsemi2N3906](https://www.onsemi.com/pdf/datasheet/2n3906-d.pdf). Validar corte, polaridad, aislamiento y comportamiento de encendido/apagado en banco; el software probado lógicamente y los taladros CAD no certifican esos ensayos.
