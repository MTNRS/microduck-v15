# Microduck V16 R1 · Banco de mandíbula G8

El kit reúne cuatro piezas en dos impresiones para la Bambu Lab P2S con boquilla de 0,4 mm. Necesitarás también P49 y P69 para las dos orejetas del MG09, la carcasa superior y el resto de la cabeza del Microduck para instalar la boca en el robot. El ensayo de banco puede hacerse con la cabeza fuera del cuello. En la escena 03 de Blender puedes ver la cabeza suelta, el MG09 y la incorporación de la mandíbula a 22°.

## Impresión

Abre el 3MF de PETG de `Placas_P2S_AMS2` y asigna el naranja del AMS 2. Incluye P34 y P36, capa de 0,2 mm y base de tres capas. Para P38 y P39 usa el proyecto naranja de TPU 95A con la bobina exterior, capa de 0,2 mm y sin base. El laminador calcula 59.12 g de PETG y 15.24 g de TPU. Las dos placas van sin pausas. Los cuatro STL sueltos conservan su orientación. Los archivos en `Para_la_P2S_laminado` incluyen el G-code de ambas placas. El informe de coincidencia vincula cada STL al modelo del 3MF y al G-code exportado.

## Herramientas y montaje

Prepara calibre, escariador de mano de 5,5 mm, llave Allen de 2 mm, punta de cruz que ajuste al tornillo del MG90S, cortador para el brazo y una mordaza pequeña de caras paralelas para el casquillo. Comprueba que el brazo del lote cabe en su alojamiento sin holgura angular excesiva. La forma del brazo y la altura del cubo varían entre proveedores.

1. Limpia las bases de impresión y los alojamientos. Con P36 suelta, termina su piloto de Ø5,35 mm con el escariador. La cota acabada del asiento es de 5,500 a 5,512 mm. Un calibre corriente sirve para las cotas generales. Para confirmar la tolerancia H7 se necesitan calibres de tapón adecuados.
2. Introduce el casquillo recto en P36. El modelo sitúa cada extremo dentro de la mejilla. Comprueba que el hombro Ø4 del tornillo gira libre dentro del casquillo ya prensado. Monta el labio inferior P38 en P36 y el superior P39 en el soporte fijo según sus asientos originales.
3. Con P34 suelta, entra desde dentro con la tuerca M3 en su alojamiento hexagonal. Coloca la arandela entre la cara fija del soporte y el futuro extremo del hombro. Presenta el núcleo con MG09 instalado. Mantén recogidos aparte los latiguillos que bajarán al cuello y monta los cuatro cierres de P33 mientras P36 está fuera.
4. Sujeta la cabeza en el banco antes de fijarla al cuello. Orienta P36 a 22° de apertura y sube la mandíbula verticalmente desde 45 mm por debajo. El rebaje de servicio permite pasar la punta del estriado sin abrir las mejillas a la fuerza. Deben quedar fuera de esta maniobra W044, W087, W096, OEM06-1, OEM06-3 y H003. Deja el cable H003 accesible hasta terminar el pivote. La escena 03 muestra la dirección sobre el robot como referencia.
5. En el lado pasivo, introduce el tornillo de hombro desde el exterior y asienta el hombro contra la arandela con la Allen de 2 mm. Gira a mano y comprueba que el casquillo sigue libre. Si el apriete frena la mandíbula, vuelve a comprobar la arandela, longitud de hombro y profundidad del alojamiento.
6. Prepara a 13,0 mm de longitud total el brazo doble suministrado con ese MG90S, con el corte repartido entre ambos extremos. Desbarba. Ajusta el servo a la posición correspondiente a la apertura de montaje y desconecta la alimentación mientras acoplas el brazo por la otra cara. Introduce su tornillo central desde fuera. Los dos tornillos M2×8 y los calces que bloqueaban la mandíbula en la revisión E se suprimen en este pivote.
7. Lleva H003 por su trazado con la cabeza ya montada, con su cubierta fuera de las caras de apriete. Comprueba a mano el recorrido completo antes de colocar la cabeza en el cuello. Los relieves de P36 reservan espacio tanto para H003 como para las cabezas de tornillo próximas.

## Carrera y calibración

El banco geométrico da 18,99 mm de luz vertical en la zona de agarre a 22°, medidos en el centro y a 9 mm a cada lado. Al cerrar, el diseño prevé aproximadamente 0,10 mm de compresión entre los dos nervios inferiores y el labio superior. A 0,15° se separan. La fuerza de agarre, la retención del brazo, la temperatura del servo y la capacidad de levantar un calcetín requieren un ejemplar físico. Calibra el cero al contacto suave.

**Ensayo en seco de la utilidad.** Ejecuta `python boca_en_banco.py --cerrado-us 1500 --abierto-us 1635`. Estos números solo ilustran la sintaxis. El programa no abre la interfaz I²C sin el argumento explícito de activación.

**Banco eléctrico independiente.** Usa un PCA9685 dedicado con su dirección 0x40, masa común entre lógica y alimentación, VCC de lógica a 3,3 V y una alimentación regulada de servo de 5 V. Conecta el MG09 únicamente en S14, con positivo en el centro y los contactos GND y señal identificados antes de energizar. Habilita I²C en Raspberry Pi OS, instala `python3-venv`, crea el entorno con `python3 -m venv --system-site-packages .venv` e instala la biblioteca con `.venv/bin/pip install adafruit-circuitpython-pca9685 adafruit-blinka`. Este modo supone OE activo en el PCA9685 de banco.

Con el brazo retirado, inicia `.venv/bin/python boca_en_banco.py --calibrar --activar-banco` para situar el eje a 1500 µs. Alinea mecánicamente la boca cerca de la mitad del arco al montar el brazo, con la alimentación del servo desconectada. Tras volver a alimentar, ajusta en pasos de 5 µs, anota el pulso de contacto suave y el de 22° medido. Pulsa q para soltar. Para probar un ciclo sustituye ambos números de ejemplo por los valores medidos y añade `--activar-banco`. El programa termina soltando S14. Detén el ensayo si el servo zumba o se frena. Mantén el robot G7 sin alimentación, según su fe de erratas.

## Comprobaciones incluidas

`Verificacion` recoge la entrada vertical frente a los sólidos de la cabeza, los seis ramales que se montan después, el acceso de las herramientas, el barrido angular ante los cables tendidos y el contacto entre los labios. El eje del servo y el casquillo tienen interfaces de acoplamiento intencionadas. La prueba de acceso representa una varilla de Ø4 mm y un mango de Ø25 mm. Las cotas nominales del servo y del brazo quedan pendientes de contrastar con tu lote de AliExpress.


## Qué imprimir si empiezas de cero

P34, P36, P38 y P39 son las cuatro piezas que salen de las dos placas naranjas. Las dos placas permiten revisar los labios, el casquillo y el pivote. Para accionar la mandíbula con el MG09 hace falta también P49 y P69, que reciben las dos orejetas del MG09, y los herrajes. Para reproducir la cabeza completa mostrada en la escena 03 utiliza el catálogo del robot. P33 es la carcasa superior, P35 el frontal, P40 el aro del ojo, P54 su soporte y P69 la mejilla. El índice permite localizar cada STL y su placa. Si ya tienes una cabeza del robot, comprueba el registro del soporte y del eje al presentar las piezas nuevas.

## Retención de los labios de TPU

El labio superior P39 asienta sobre P34 y el inferior P38 sobre P36. En CAD el inferior puede levantarse verticalmente 5 mm. Los nervios de mordida hacen contacto con el labio opuesto al cerrar y dejan libre el movimiento al abrir. Para la prueba a mano presenta ambos labios en seco. Para sujetar tela, los dos necesitan retención sobre sus asientos.

Para el ensayo he seleccionado LOCTITE 435, un cianoacrilato tenacificado para plásticos y elastómeros. Henkel documenta la unión en película fina y el curado durante al menos 24 horas. La ficha carece de datos de resistencia específicos para tu combinación de PETG y TPU 95A impresos. Pega primero dos recortes de los mismos filamentos, con la misma cara de impresión que las piezas, y comprueba tras el curado si el TPU se despega por un borde. Si se despega fácilmente, deja las pruebas con carga pendientes. [Ficha técnica de Henkel](https://datasheets.tdx.henkel.com/LOCTITE-435-en_GL.pdf)

Con los dos conjuntos fuera del robot, limpia y seca las superficies según la ficha. Protege el eje, el casquillo y la cara de agarre. Aplica una película fina de adhesivo en un solo lado de cada unión y presiona cada labio contra su propio asiento. Déjalos curar por separado durante al menos 24 horas. Retira las protecciones y comprueba que los labios tocan antes que las piezas rígidas. Calibra después los dos extremos del servo. Para el primer agarre usa una sola capa del calcetín, sobre una mesa, aumentando la carga poco a poco. Registra la masa del calcetín que levanta el ejemplar y si alguno de los bordes se despega.
