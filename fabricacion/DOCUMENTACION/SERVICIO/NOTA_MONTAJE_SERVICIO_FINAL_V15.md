# Servicio del kit V15 R2 final

Fuente comprobada: `KIT_V15_R2_FABRICACION/ASSEMBLY_FABRICACION_CANDIDATO_V15.json`, SHA `d1e061923094f4cd2fcfbbeb800a2daeffc9b78ee9077f8575ebd8b72b0ccbb4`.

Para abrir el cassette trasero, retirar los cuatro tornillos M2x25 junto con sus arandelas de cabeza. Las cuatro tuercas cautivas permanecen montadas en el frontal fijo: no se extraen ni se desplazan con la tapa. Desconectar los cables que cruzan entre módulos y aparcar los conectores sueltos fuera del corredor. Los componentes marcados `rear_lid` permanecen montados sobre la tapa. Extraer el módulo completo recto hacia −X, sin bascular ni forzar. El recibo incluye expresamente las cuatro tuercas como obstáculos fijos.

El servicio de la cubierta de cabeza se ha comprobado mediante elevación rígida hacia +Z tras retirar sus cuatro cierres. Los elementos, cables y secuencia de desmontaje deben seguir la guía de montaje completa; la prueba no incluye esfuerzos ni un barrido de cables flexibles.

Los recibos `CASSETTE_EXTRACCION_RAW_FINAL.json` y `CABEZA_SERVICIO_RAW_FINAL.json` conservan los resultados RAW: cuatro contactos diminutos en el cassette y uno en la microjunta de cabeza. Sus calificaciones superficiales están separadas, enlazadas por SHA al mismo kit y no sustituyen el resultado de cero exacto. No se han aumentado umbrales ni recortado la forma aprobada para eliminar esas películas numéricas.

La forma del torso y la cabeza se compara en `FORMA_APROBADA_FINAL.json`; los contornos no equivalen a igualdad de todos los triángulos. El resumen `RESUMEN_SERVICIO_Y_FORMA_FINAL_V15.json` reúne las fuentes, hashes y límites.

Verificar ajuste, accesibilidad, desconexión de conectores y deslizamiento en la primera unidad física. Estas pruebas son geométricas nominales; no acreditan fuerza de extracción, tolerancias de impresión, fatiga del arnés ni funcionamiento cargado.
