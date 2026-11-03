# CAD, vistas y auditorías

## Restaurar el archivo de Blender

Ejecuta estos comandos desde la raíz del repositorio con Python 3.

```console
python tools/verify_repo.py
python tools/restore_cad.py
```

La primera orden comprueba los archivos del repositorio. La segunda reúne las partes GZIP de `cad/`, verifica sus SHA-256 y reconstruye `cad/Microduck_V15_R2_PUBLICO.blend`. La huella del `.blend` restaurado debe coincidir con la del montaje público guardado, `a465c42346cfdcfb609c7b509ed14e586b0315916f60b3d3c4202c541da85174`. El restaurador rechaza un destino existente con contenido distinto. El `.blend` reconstruido está ignorado por Git. [Manifiesto del CAD](../cad/manifest.json) · [Restaurador](../tools/restore_cad.py) · [Verificador](../tools/verify_repo.py)

Para editar, puedes restaurar directamente una copia de trabajo y abrirla en Blender. También puedes abrir el archivo restaurado y usar **Archivo → Guardar como**.

```console
python tools/restore_cad.py --output cad/Microduck_V15_R2_TRABAJO.blend
```

## Trabajar con el montaje

La edición pública incluye sólo la escena V15 R2. La placa goBILDA 3108-2827-0801 está representada por una envolvente dimensional propia que conserva su ubicación. Las 80 piezas imprimibles, sus poses y sus ejes se comprobaron tras guardar y reabrir el archivo. [Verificación del CAD público](../verificacion/BLENDER_EDICION_PUBLICA.json)

Localiza las piezas por nombre en el Outliner. Oculta temporalmente las carcasas para revisar tornillería, placas y espacio de acceso. El manifiesto de montaje distingue `PRINT` para piezas impresas, `REFERENCE` para componentes y herrajes, y `KEEPOUT` para reservas de espacio. En una revisión nueva, toma los ejes, los orígenes y la escala como referencia para los cambios. Vuelve a comprobar encaje, recorridos y exportación de las piezas afectadas antes de sustituir un STL del kit.

Para imprimir R2, usa los STL de `STL_POR_COLORES` y sus proyectos de impresión cuando correspondan. El manifiesto STL fija las huellas, las unidades en milímetros y la orientación de cada pieza. Las pausas y los soportes pertenecen a esa configuración de impresión. [Manifiesto de montaje](../verificacion/ASSEMBLY_FABRICACION_V15.json) · [Manifiesto STL](../fabricacion/STL_MANIFIESTO_V15.json) · [Soportes y pausas](../fabricacion/SOPORTES_Y_PAUSAS_V15.json)

## Vistas del kit

Las capturas están incluidas en `fabricacion/` y corresponden a la auditoría nominal anterior a la preparación del CAD público.

| Vista | Qué muestra | Archivo |
| --- | --- | --- |
| General | Conjunto en posición de montaje | [Vista general](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_general.png) |
| Sección | Componentes montados con carcasas ocultas | [Componentes en sección](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_componentes_seccion.png) |
| Despiece | Cassette trasero desplazado 85 mm hacia −X y cubierta superior de cabeza elevada 50 mm hacia +Z para ver ambos módulos | [Módulos separados](../fabricacion/DOCUMENTACION/VISTAS/V15_R2_modulos_separados.png) |

La secuencia de servicio y los cierres que se retiran están en la guía de montaje. [Guía de servicio de cassette y cabeza](../fabricacion/DOCUMENTACION/SERVICIO/NOTA_MONTAJE_SERVICIO_FINAL_V15.md)

## Leer las auditorías

- **Integridad del montaje.** La relectura del archivo histórico usado en la auditoría compara geometría, matrices, parentesco y expresiones de los drivers. [Verificación del Blender guardado](../fabricacion/DOCUMENTACION/VERIFICACIONES/BLENDER_DATOS_GUARDADOS_VERIFICADOS_V15.json)
- **Encaje estático.** El informe RAW conserva los volúmenes de intersección. La clasificación complementaria comprueba si las regiones de contacto admiten un cubo de 0,01 mm de lado. Los 236 pares clasificados del kit final quedan por debajo de esa escala de rasgo. [Auditoría estática RAW](../fabricacion/DOCUMENTACION/VERIFICACIONES/ESTATICA_GLOBAL.json) · [Clasificación de contactos](../fabricacion/DOCUMENTACION/VERIFICACIONES/CLASIFICACION_CONTACTOS.json)
- **Forma y servicio.** El recibo final enlaza el SHA del kit, los contornos comparados, el barrido del cassette hacia −X y la elevación de la cubierta de cabeza hacia +Z. Las cuatro tuercas cautivas del frontal se incluyen como obstáculos fijos. Se conservan los cinco contactos superficiales RAW y sus calificaciones por separado. [Resumen de servicio y forma](../fabricacion/DOCUMENTACION/VERIFICACIONES/RESUMEN_SERVICIO_Y_FORMA_FINAL_V15.json)
- **Recorridos y primera unidad.** Los rangos CAD se expresan como deltas respecto a la pose de referencia. El ajuste físico, la calibración de los servos y el funcionamiento con carga se comprueban en la primera unidad. [Rangos geométricos comprobados](../fabricacion/DOCUMENTACION/CALIBRACION/CAD_RANGOS_VERIFICADOS_V15.json)

La procedencia de las mallas, planos y componentes de referencia se recoge por fuente. [Fuentes y licencias](../SOURCES.md)
