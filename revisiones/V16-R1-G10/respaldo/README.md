# Respaldo de desarrollo de Microduck V16

El ZIP principal de G10 se abre directamente. Contiene el robot de esta revisión, los archivos de impresión, las fuentes de las placas, las guías, el proyecto de Blender y las verificaciones. [Descargar el Microduck completo](https://github.com/MTNRS/microduck-v15/releases/download/v16-r1-g10/Microduck_G10_completo_P2S.zip)

El respaldo adicional conserva los archivos del proyecto V16 y de sus revisiones anteriores, los generadores auxiliares, los resultados de pruebas y la simulación de Isaac. Los pesos y los resultados de entrenamiento corresponden a sus propias versiones de simulación. La G10 de fabricación tiene verificaciones mecánicas y de laminado. La marcha y la recuperación con este nuevo montaje requieren ensayos independientes.

El índice conserva la ruta y el SHA-256 de cada archivo. Si varias revisiones comparten exactamente los mismos bytes, el índice apunta a una sola copia. Algunos paquetes antiguos están en las publicaciones G8 y G9. Las cachés de Python y los bloqueos o archivos temporales de ejecución se omiten. Las herramientas de terceros se instalan por separado.

Descarga el script de esta carpeta y ejecútalo con Python 3.11 o posterior. Para restaurar la simulación de Isaac con sus scripts, modelos y resultados, usa

    python restaurar_microduck.py Microduck --prefijo simulacion/

Para recuperar todo el proyecto, usa

    python restaurar_microduck.py Microduck

El script descarga los bloques públicos que necesita y comprueba la longitud y el SHA-256 antes de colocar cada archivo. Conserva las descargas en descargas_microduck para reutilizarlas. Si encuentra un archivo local diferente en el destino, se detiene. Con --verificar lee y comprueba el contenido sin instalarlo. El respaldo corresponde al estado del proyecto al crear el índice.
