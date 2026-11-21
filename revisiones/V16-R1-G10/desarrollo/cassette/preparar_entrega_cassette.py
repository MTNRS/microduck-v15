from pathlib import Path
import json,hashlib,shutil,csv,math,re
r=Path('microduck-v16').resolve();k=r/'V16_R1_G10_Ensayo_P45';g=r/'V16_R1_G10_Ensayo_de_cassette';old=r/'V16_R1_G9_Ensayo_de_cierre';v=g/'Verificacion';h=r/'trabajo/cierre_G9';ev=r/'trabajo/arnes_polaridad/arnes_15_motores/evaluacion_Tendido_G10_cassette'
rd=lambda f:json.loads(f.read_text('utf8'))
def rows(f):
 with f.open(encoding='utf-8-sig',newline='') as fh:return list(csv.reader(fh,delimiter=';'))
def wr(f,rows):
 with f.open('w',encoding='utf-8-sig',newline='') as fh:csv.writer(fh,delimiter=';').writerows(rows)
def note(f,x):f.write_text(x.strip()+'\n','utf8')
for a,b in ((ev/'Holguras_cables.json','Holguras_del_arnes_15_motores.json'),(ev/'Verificacion/Electronica_contra_arnes.json','Electronica_ante_arnes_15_motores.json'),(ev/'Verificacion/Encaje_de_conectores_y_empalmes.json','Conectores_y_empalmes_15_motores.json'),(h/'Tendido_G10_cassette_barrido_entrada_10.json','Cierre_P86_153_cables.json'),(h/'P86_insercion_tornillos_exacta.json','Entrada_de_los_cuatro_tornillos_P86.json')):shutil.copyfile(a,v/b)
piece=next((g/'STL_POR_COLORES').rglob('45_*.stl'));idx=rows(old/'Indice_STL_y_placas.csv');rw=next(x for x in idx if x[0]=='P45');rw[2]=str(piece.relative_to(g));rw[-1]=hashlib.sha256(piece.read_bytes()).hexdigest();wr(g/'Indice_STL_y_placas.csv',idx)
pl='AZUL_CIELO_PETG_0p1_R3_COMPACTA';job=rd(v/(pl+'.json'));o=rows(old/'Orden_de_impresion.csv');next(x for x in o if x[0]==pl)[3]=f"{job['gramos']:.2f}";wr(g/'Orden_de_impresion.csv',o);gm=sum(float(x[3]) for x in o[1:]);blue=sum(float(x[3]) for x in o[1:] if x[0].startswith('AZUL_CIELO'))
m=rows(old/'Lista_de_materiales.csv');mr=next(x for x in m if x[0]=='AZUL_CIELO_PETG');mr[2]=f'{blue:.2f}';mr[3]=f'{math.ceil(blue*1.15)} g';wr(g/'Lista_de_materiales.csv',m)
j=rd(g/'Tendido_15_motores_en_ensayo.json');ws={w['id']:w for w in j['hilos']};changed=rd(v/'Cassette_G10_en_Blender.json')['cables_actualizados']
table=rows(old/'Ramales_y_sobrantes.csv')
for row in table[1:]:
 if row[0] in changed:row[5]=str(round(ws[row[0]]['longitud_trazada_mm'],2))
wr(g/'Ramales_y_sobrantes.csv',table)
tab=rows(old/'Latiguillos_de_los_15_MG90S.csv')
for row in tab[1:]:
 ns=['OEM'+row[0][2:]+'-'+str(n) for n in (1,2,3)]
 if not set(ns)&set(changed):continue
 lengths=[float(ws[n]['longitud_trazada_mm']) for n in ns];row[3:8]=[f'{x:.1f}' for x in [*lengths,max(lengths),max(lengths)-min(lengths)]]
wr(g/'Latiguillos_de_los_15_MG90S.csv',tab)
f='Ajuste_de_los_latiguillos.md';s=(old/f).read_text('utf8');s=re.sub(r'En la boca MG09 los recorridos.*? mm\. Estas medidas', 'Las longitudes por vía de MG09 y MG14 figuran en la tabla actualizada de esta revisión. Estas medidas',s);note(g/f,s)
status='G10 de ensayo. Quedan 24 pares de fundas con solapamiento y 31 avisos frente a envolventes de electrónica o herrajes. Mantén el pack desconectado durante la presentación.'
for sub in ('Placas_P2S_AMS2','Para_la_P2S_laminado'):note(g/sub/'ESTADO_DE_ESTA_REVISION.txt',status)
guide="""# Presentar el cassette P45 y el hilo de equilibrado BM

Con el pack desconectado, abre la escena 10 para ver la curva amarilla de W003 en el canal azul. En la escena 06 puedes reproducir la entrada completa de la placa de protección. La escena 07 muestra el despiece de las 86 piezas.

1. Identifica el pad BM por la serigrafía de la HX-2S-D20. La foto de Mantech lo sitúa en la esquina del mismo borde corto que P+ y P−. Los centros de soldadura en el CAD son estimaciones sobre la foto. El fabricante indica 46 × 20 × 3,6 mm.
2. Prepara la salida de W003 con funda de diámetro exterior máximo de 1,10 mm según el diseño nominal. Desde el pad, forma el cable hacia el borde lateral más cercano de la PCB. El tramo modelado hasta que vuelve al mazo mide 11,70 mm. La curva tiene un radio mínimo aproximado de 2,77 mm. Presenta el hilo en el canal con el resto del ramal libre.
3. Con la placa de protección y P45 aún en el banco, inicia la entrada de la placa a +28 mm en Y y −62 mm en Z respecto del asiento. Acércala a +4 mm en Y y −1 mm en Z, y termina de asentarla. Los ejes corresponden a Blender. La funda pasa a 0,47 mm de P45 en el barrido nominal. Comprueba que la placa asienta sin empujar el hilo con una herramienta.
4. Presenta P83 desde el lateral y después P65 desde abajo. El tramo formado de W003 conserva al menos 4,00 mm ante P83 y 1,80 mm ante P65 durante sus entradas. Conecta el otro extremo de W003 al adaptador de equilibrado una vez colocadas las piezas. Consulta Montaje_del_cassette.md para el resto de componentes.

El canal y el recorte de la pestaña interior liberan 17,71 mm³. La pieza queda en un solo sólido cerrado. Todo el material retirado está a más de 5,73 mm de la envolvente exterior aprobada. Esa distancia se midió hasta el contorno exterior del robot. El muestreo conserva el 99,996 % del apoyo entre P45 y P65 y el 100 % del apoyo muestreado con P83. Las medidas son de CAD. La rigidez del mazo y la posición del estaño dependen del montaje físico.

La foto y las medidas exteriores proceden de la [ficha Mantech de la HX-2S-D20 250040](https://mantech.co.za/datasheets/products/hx-2s-d20_250040.pdf). El espesor nominal de laminado de 1,4 mm y la posición de los pads son hipótesis del modelo. El informe Comprobacion_de_cinco_pads_PCM.json documenta ambas. W004 llega al portafusible junto al borde de la placa, con holgura nominal nula en el extremo al representar la funda completa. Este punto requiere corrección o verificación de la terminación real.
"""
note(g/'Montaje_del_canal_BM.md',guide)
f='Montaje_del_cassette.md';s=(old/f).read_text('utf8');s=s.replace('Trabaja con el pack desconectado.','Trabaja con el pack desconectado. Sigue también [la salida BM de G10](Montaje_del_canal_BM.md) al instalar la placa en P45.');note(g/f,s)
f='Montaje_de_P86.md';s=(old/f).read_text('utf8').replace('persisten 29 pares','persisten 24 pares');note(g/f,s)
f='LEEME.md';s=(old/f).read_text('utf8').replace('Microduck V16 R1 G9 · Ensayo de cierre','Microduck V16 R1 G10 · Ensayo de cassette').replace('Microduck_G9_arnes_y_montaje.blend','Microduck_G10_arnes_y_montaje.blend').replace('711.24 g',f'{gm:.2f} g').replace('La G9 sustituye P86. Las otras 85 mallas corresponden a la G8.','La G10 sustituye P45. Las otras 85 mallas corresponden a la G9.').replace('El diseño del cassette P45 y la envolvente del torso siguen la geometría aprobada.','P45 incorpora un canal interior para BM. Se conserva la envolvente aprobada del torso.').replace('tiene 29 pares','tiene 24 pares')
s=s.replace('**Tapa P86.**','**Cassette P45.** La escena 10 de Blender muestra por dónde pasa el hilo BM. La escena 06 reproduce la entrada de la placa. Consulta [el montaje del canal](Montaje_del_canal_BM.md).\n\n**Tapa P86.**')
note(g/f,s)
note(k/'LEEME.md',"""# P45 de ensayo para la Bambu Lab P2S

El proyecto contiene un solo cassette P45 en PETG azul cielo. Boquilla de 0,4 mm, capa de 0,10 mm, base de tres capas y consumo estimado de 35,04 g. La pieza se imprime sin pausas. Abre el proyecto en Placas_P2S_AMS2 para inspeccionarlo o el archivo de Para_la_P2S_laminado para imprimirlo. Asigna el PETG al color correspondiente del AMS 2.

Para comprobar el cassette ya impreso, sigue Montaje_del_canal_BM.md. La prueba mecánica se hace con el pack desconectado. El resto del robot y el montaje eléctrico siguen en revisión.""")
for f in ('Montaje_del_canal_BM.md','Montaje_del_cassette.md','Canal_BM_de_P45.png'):shutil.copyfile(g/f,k/f)
for f in ('Entrada_con_cable_BM_formado.json','Comprobacion_de_cinco_pads_PCM.json'):shutil.copyfile(v/f,k/'Verificacion'/f)
print('masa total',gm,'placas',len(o)-1,'cables actualizados',len(changed))
