# Arnés V15: conexiones y tendido de primera unidad

Kit exacto: d1e061923094f4cd2fcfbbeb800a2daeffc9b78ee9077f8575ebd8b72b0ccbb4. El [registro de conexiones y corte](CONEXIONES_Y_CORTE_ARNES_V15.csv) define cada extremo, red y polaridad. **Mide la longitud en la primera unidad antes de cortar.** Las reservas del CAD no son un arnés completo probado. No uses el mapa histórico MAPA_15_SERVOS_ARNES_V15.json: su propuesta confundía índice físico de servo y canal PCA.

| Desde | Hasta | Regla |
|---|---|---|
| XT30 pack + / − | PCM B+ / B− | Crudo. Confirmar polaridad y serigrafía del 250040 entregado. |
| XH3 pack | B3B-XH-A robot | Sólo pin 2 → PCM.BM. Pines 1 (B−) y 3 (B+) aislados sin conexión en el robot. |
| PCM P+ | MINI 5 A → HP VIN | Terminales directos; no usar una pista FR4 para potencia. El fusible protege, no regula corriente. |
| HP VOUT | D24 VIN, D36 VIN, divisor ADS | D36 en FRONT; el resto en tapa. |
| PCM P− | HP, reguladores, PDB y toda masa lógica | Retorno protegido común. No unir a B− ni usar la Pi como retorno de servos. |
| D24 VOUT 5 V / P− | PDB XT30 + / − | Potencia de servos. |
| D36 VOUT 5 V / P− | Pi J8 físico 2 / 6 y pies | Pin 2 físico es 5 V, no BCM2/SDA. |
| HP A / B | Dos terminales del reed | Contacto seco sin polaridad. El imán se aproxima y retira. |

Para carga, retira el pack y desconecta XT30 y XH3 del robot. Cargador externo: XT30 crudo B+/B− y XH3 1=B−, 2=BM, 3=B+. Sigue [el plan de puertos](../PORT_PLAN_K10_V15.md): LiIo 2S Balance CHG, 4.1 V/celda, 0.3 A nominal. La PCM del robot queda fuera del circuito de carga. Si se alimenta Pi por USB en servicio, aislarla del pack, de la salida D36 y de posibles retroalimentaciones por el arnés.

| Pi J8 físico | Función | Otro extremo |
|---:|---|---|
| 1 | 3V3 | PCA VCC, BNO VIN, ADS VDD, emisor Q1 y pull-ups de base/OE. |
| 3 / 5 | SDA BCM2 / SCL BCM3 | I²C 3.3 V: PCA 0x40, BNO 0x28 y ADS 0x48; conservar selecciones de dirección. |
| 6 | GND | P− protegido, común a PCA/BNO/ADS/control. |
| 11 | BCM17 | ADS ALERT activo LOW. |
| 29 | BCM5 | PCA OE, HIGH deshabilita. Retirar R7 a GND de PCA RevC, poner 10 kΩ OE→3V3. |
| 15 / 13 | BCM22 / BCM27 | Señal del pie izquierdo/derecho. |

Control: HP.VOUT → 20 kΩ → ADS.AIN0 → 10 kΩ → P− (divisor 0.1%). ALERT → 10 kΩ → base Q1; base → 10 kΩ → 3V3; emisor → 3V3; colector → 4.7 kΩ → HP.OFF; OFF → 100 kΩ → P−. Verifica el patillaje real de Q1 2N3906. PCA sin headers PWM altos ni potencia en V+. BNO recibe 3V3 por VIN, no por la salida 3Vo. Comprueba pull-ups y niveles del bus con las tres placas.

Cada pie usa dos Omron SS-01-E: los dos NO a S, los dos COM a P−; NC aislado. D36.5V → 2.2 kΩ → S → 10 kΩ → GPIO → 20 kΩ → P−. El cierre de cualquiera lleva S a masa. Salen tres hilos por pie: 5 V, P− y GPIO; medir el nivel dividido antes de conectarlo. Nunca aplicar 5 V directamente a un GPIO.

## Servos

Cada adaptador Y lleva V+ y GND exclusivamente del PDB y señal exclusivamente del PCA; su extremo de tres contactos conserva el enchufe OEM. Deja vacío S en el PDB y apaga Signal Sharing. Etiqueta P00…P13 en las tomas de potencia libres verificadas por continuidad y registra su posición física. Estas etiquetas no son los ocho canales internos del fabricante. No deduzcas polaridad por color. P14 y la otra toma quedan libres; PCA 15 tampoco se conecta.

| Etiqueta | PCA | Servo físico | Articulación | Potencia | Estado |
|---|---:|---:|---|---|---|
| S00 | 0 | 00 | left_hip_yaw | P00 | Conectar |
| S01 | 1 | 02 | left_hip_roll | P01 | Conectar |
| S02 | 2 | 04 | left_hip_pitch | P02 | Conectar |
| S03 | 3 | 03 | left_knee | P03 | Conectar |
| S04 | 4 | 05 | left_ankle | P04 | Conectar |
| S05 | 5 | 06 | neck_pitch | P05 | Conectar |
| S06 | 6 | 07 | head_pitch | P06 | Conectar |
| S07 | 7 | 08 | head_yaw | P07 | Conectar |
| S08 | 8 | 10 | head_roll | P08 | Conectar |
| S09 | 9 | 01 | right_hip_yaw | P09 | Conectar |
| S10 | 10 | 11 | right_hip_roll | P10 | Conectar |
| S11 | 11 | 13 | right_hip_pitch | P11 | Conectar |
| S12 | 12 | 12 | right_knee | P12 | Conectar |
| S13 | 13 | 14 | right_ankle | P13 | Conectar |
| S14 | 14 | 09 | jaw | P14 vacío | Desconectado |

## Tendido y corte

1. Con batería fuera, prepara XT30 y BM como conexiones separadas y polarizadas. Aísla bornes del fusible y ambas caras del FR4 de control. Pasa los dos hilos del reed por sus ojos sin cargar sus terminales. Sigue [el orden de placas](../DAG_MONTAJE_ELECTRONICA_V15.md) con cables desconectados y aparcados en cada inserción.
2. Presenta D36 y su alimentación en FRONT antes de MG00/01. Deja accesible el cruce trasera→FRONT para desenchufarlo antes de extraer la tapa. Lleva 5 V lógica, P−, I²C, OE, ALERT y señales de pie hacia la Pi por el paso del cuello. Sujeta aparte los ramales de servos de cuello/cabeza, con holgura en cada eje. Deja libre la microSD.
3. Dentro de la tapa, usa los primeros codos de D24→XT30/PDB y PDB→adaptadores y los ojos de positivo, retorno, señales PCA y baja potencia. Soldar los pigtails PCA por detrás y sujetarlos antes de la primera curva. Mantén los tramos de potencia alejados de señales, asientos de cierre y envoltura de celdas.
4. Baja por cada lado del torso a los servos de pierna, junto a sus caras protegidas y con un bucle por eje cruzado. Los tres hilos de cada pie salen por el pasacables del talón, suben por su pierna y entran a FRONT por los pasos de las tapas inferiores, con seis hilos en el corredor central de pies. No uses el hueco del engrane como pasacables.
5. Presenta cada cable real sin cortar. Comprueba retirada de tapa y conectores; recorre manualmente los límites calibrados con el robot sin alimentar, incluidas las combinaciones pertinentes. El roll de ambas caderas se limita a ±10° CAD respecto a STAND. El bucle no debe tirar de un terminal ni alcanzar engranes, brazos, topes, rodamientos o juntas. Añade la cola de crimpado/soldadura, corta y registra cada Wxxx sólo tras esta prueba. La salida y longitud OEM dependen del lote.
6. Prueba continuidad de cada red y ausencia de puentes involuntarios entre B−/P−, los dos 5 V, 3V3 y PWM con módulos aislados; la conducción normal de la PCM no identifica un puente de cableado. Con fuente limitada y servos desconectados, verifica polaridad, niveles, OE durante arranque, parada ADC, los pies y respaldo PCM por celda. Luego mide caída y temperatura con carga gradual; no aumentes el fusible para evitar disparos.

Las longitudes, la liberación de conectores, la holgura del arnés con movimiento y la capacidad bajo carga quedan pendientes de primera unidad. El CSV no autoriza otro conector sin comprobar su volumen real.
