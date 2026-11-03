# Puertos de batería y carga

Hay dos masas distintas que no se deben unir por un cargador: **B− es el negativo crudo de las celdas; P− es la salida protegida de la PCM**. Todas las masas del robot, Pi, reguladores y ADC van aP−. La ficha del250040 no publica un procedimiento de conexión por etapas; el montador debe validar la conexión y desconexión deB+/B−/BM para esa revisión concreta.

El pack extraíble lleva salida principal **XT30, B+ yB− crudos**, y balance **JST-XH3, pin1=B−, pin2=BM, pin3=B+**. Pin1 significa la cavidad marcada de la carcasa; no se define por izquierda/derecha mirando una fotografía. Los contactos energizados del pack quedan hembra, aislados y con tapa de transporte. El cuerpo terminado y los extremos del cable se encargan juntos al montador; no se usa un portapilas de muelles.

En el lado robot, XT30 va únicamente aB+ yB− de la PCM. Del conector de balance sólo se utilizaBM/pin2; los contactos1y3 del adaptador del robot quedan **sin conectar y aislados**. Así no se introduce una conexión adicional del robot alB− crudo. La mitad macho/adaptador deBM y su alivio de tensión necesitan comprobarse en el arnés: la reserva de capacidad del CAD no acredita por sí sola un conector completo fabricado.

P+ de la PCM pasa por MINI5A y luego alHP2813; P− retorna al robot. El divisor ADS1115 tomaHP.VOUT yP−, y se apaga conHP. El reedA–B es un mando, no un aislador físico de los puertos de las celdas.

**Carga fuera del robot:** desconectar físicamente las dos interfaces del pack y retirarlo. Alimentar primero el cargador y conectar después el adaptador principal y el balance, comprobando polaridad y tensiones. No conectar simultáneamenteP− del robot yB− del balanceador: las masas comunes del cargador podrían puentear la protección de lado negativo. Durante esta carga el pack crudo queda controlado por el cargador balanceador; **no se atribuye protección de carga a la PCM del robot**.

Selección externa nominal de raíz: **SkyRCB6neo+, modeloSK100211**, `LiIo`, `2S`, `Balance CHG`, **0.3A** y **4.1V/celda**(8.2V total). La tolerancia publicada±0.2A deja hasta0.5A, la carga estándarK10. El máximo nominal de1Ah de la celda corresponde a su ciclo especificado de4.2V; con4.1V se renuncia a parte de esa energía y no se promete autonomía. Se usa el modoLiIo sin forzar un perfilLiPo de4.2V. Fuente primaria: [manualSkyRCV112](https://www.skyrc.com/download/B6neo%2B_100211_Instruction%20Manual_250319_V.112.pdf).

La alimentación USB de servicio de Pi sólo se usa con **XT30 ybalance del pack desconectados**. Antes de energizar el conjunto faltan la inspección del pack soldado, verificación de todas las polaridades, validación del250040, arnés y disparoADC/PNP/HP. Este plan fija los nodos eléctricos; no afirma que esas pruebas ya se hayan hecho.
