# Soporte BM: FR4 de 8 × 9,8 × 1,6 mm

Plano extraído del REF congelado `V15_BM_CUSTOM_FR4`, SHA `1618aa282a5bdd0dfec6d611504226c438532bdfe1f878061bdd4f85aafbc09a`. No modifica el CAD ni la posición del conector.

Usar `BM_FR4_CORTE_TALADROS_1a1.svg` o el DXF en milímetros. Imprimir al **100 %**, sin ajustar a página; comprobar la barra de 10 mm. La PNG es una ampliación para consulta y no sirve como plantilla de escala.

La vista mecánica mira desde **−Y**, cara del header. Origen en la esquina inferior izquierda; +X a la derecha y +Z arriba. El contorno mide 8,00 × 9,80 mm y la placa terminada es nominalmente de 1,60 mm. Taladrar tres agujeros de Ø1,00 mm, centros (3,475; 2,450), (3,475; 4,950) y (3,475; 7,450) mm. La muesca izquierda ocupa X 0…0,70 y Z 6,90…8,50 mm; terminar sus esquinas con lima para que entre la llave de captura. No añadir el chaflán de una revisión antigua.

El SVG de cobre muestra la **cara +Y**, por lo que su vista está espejada respecto al corte. Retener tres islas separadas de Ø2 mm. Solo la isla central se une mediante una pista de 0,6 mm a la isla de soldadura de Ø1,6 mm; esta última queda en (1,925; 4,950) de la vista mecánica. La separación nominal mínima entre islas es 0,50 mm. El SVG es la vista física de la cara de cobre, no una orden de espejo automática para cualquier método de transferencia.

1. Cortar FR4 de una cara y terminar bordes/muesca. Taladrar con la placa sujeta; limpiar y comprobar con el header real sin forzarlo. Medir el espesor acabado antes de insertar el conjunto en sus guías.
2. Aislar completamente las tres islas. Comprobar continuidad **solo con el adaptador suelto, sin batería ni PCM conectados**: centro a su cable BM sí; centro a cada extremo y extremo a extremo no.
3. Soldar el JST B3B-XH-A apoyado sobre la placa. Solo el pin central 2 lleva cable a BM del PCM. Los dos extremos quedan NC; no conectarlos a masa protegida ni entre sí. El XHP de la batería lleva tensiones sin proteger y sus extremos pueden quedar activos aunque no tengan cable en esta placa.
4. Preparar solo las colas libres del header: longitud total nominal 2,4 mm desde su cara de apoyo; con FR4 de 1,6 mm quedan 0,8 mm. Desbarbar y revisar puentes de soldadura. No cortar postes de acoplamiento ni plástico.
5. Cubrir las islas/puntas NC y el cobre que pueda tocar herrajes con aislamiento eléctrico fino, sin obstruir el conector ni la muesca. Mantener la soldadura y la protección dentro de la tapa prevista; comprobar con calibre/primera unidad, no acumular capas sin medir.
6. Sacar el cable BM por la ventana prevista, montar placa/header en la tapa y cerrar la llave de captura. Instalar este conjunto con la LID vacía según `BM_STAGED_ASSEMBLY_PROOF_R2_V15.json`; después colocar los demás módulos. Comprobar pinout/polaridad con el procedimiento eléctrico POWER antes de enchufar el pack.

El plano verifica contorno y centros contra el NPZ real; los círculos de taladro son nominales de fabricación. El cobre es la definición del circuito propio, no una PCB comercial. La calidad de soldadura, el ajuste físico, la identificación del cableado del pack y las fuerzas del conector requieren primera unidad.
