# Caderas V15: límite CAD y piezas congeladas

Overlay: `OVERLAY_HIP_ROM10_PRINT_RELIEFS_FROZEN_V15.json`, SHA `144b38920261231224446755109fe4b2980fad085dd2e896e0656c8a67c6e011`. Sustituye ocho piezas impresas completas; incluye los bolsillos D36 de las dos tapas de servicio. No añade tornillos, piezas de metal ni cambios en las posiciones de servos, rodamientos, placas o ejes. FRONT y LID principales conservan su forma.

El límite **CAD relativo a STAND** de `left_hip_roll` y `right_hip_roll` es **±10°**. Se verificaron también hip yaw±15° y combinaciones simétricas de±5°/±10°. Son30 poses discretas y326 booleanos sobre los archivos F32 definitivos:0 contactos y0 desconocidos. No constituye un barrido continuo de todo el espacio articular ni una calibración del servo.

No se adoptan las piezas experimentales de `hip-ROM-land/`: se descartaron los cambios de land y hardware. Las piezas activas están únicamente en `hip-ROM10-frozen-v1/` y su manifiesto. Se conservan las longitudes M2x12 y las pilas de arandelas/tuercas originales.

Se mantuvo el stock protegido de los asientos M2 y el barril nominal de2.3mm entre facetas paralelas. El suplemento `HIP10_BARREL_PARALLEL_FACET_SUPPLEMENT.json` enlaza la geometría exacta. El stock de pared C2 protegido a1.2mm presenta residuos numéricos de9.13e−10/9.40e−14mm³; no se han abierto nuevas zonas de esa pared mediante estos bolsillos.

A±15° de roll hacia fuera persiste un conflicto real entre el conjunto M2 fijo y el asiento plano M2 de CAP04/CAP13. `HIP_ROM_EXACT_M2_STOCK_BLOCKER.json` conserva el testigo:0.3699mm³ de metal contra ese asiento protegido en la alternativa land descartada. Recortar ese apoyo para afirmar±15° eliminaría stock de apriete. Por eso no se certifica ese recorrido.

Tres diferencias de volumen de Manifold son negativas y se conservan como **NUMERIC_VOLUME_UNQUALIFIED**. No se convierten a cero. La representación se acota mediante la construcción nominal por sustracción y el límite de redondeo IEEE/F32, máximo6.61e−6mm; los dos ciclos de cada una de las ocho mallas conservan un sólido cerrado, sin aristas o áreas nulas. No se afirma igualdad volumétrica exacta.

La calibración deberá respetar el límite CAD antes de mover el robot. Un MG90S de180° no concede180° de recorrido a cada articulación del conjunto. No se fijan pulsos, signo, topes físicos, carga admisible o marcha sin medir la primera unidad.
