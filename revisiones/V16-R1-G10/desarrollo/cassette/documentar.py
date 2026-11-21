from pathlib import Path
import tempfile,shutil,json,csv,hashlib,zipfile,math
r=Path('microduck-v16').resolve();g=r/'V16_R1_G9_Ensayo_de_cierre';v=g/'Verificacion';rep=r/'V16_R1_G9_Reposicion_P86';base=r/'V16_R1_G8_Ensayo_de_montaje';w=r/'trabajo/cierre_G9';ev=r/'trabajo/arnes_polaridad/arnes_15_motores/evaluacion_Tendido_G9_tapa_comprobada'
def load(f):return json.loads(f.read_text('utf-8-sig'))
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rows(f):
 with f.open(encoding='utf-8-sig',newline='') as p:return list(csv.reader(p,delimiter=';'))
def wr(f,s):
 with f.open('w',encoding='utf-8-sig',newline='') as p:csv.writer(p,delimiter=';').writerows(s)
for f,to in ((ev/'Holguras_cables.json','Holguras_del_arnes_15_motores.json'),(ev/'Verificacion/Electronica_contra_arnes.json','Electronica_ante_arnes_15_motores.json'),(ev/'Verificacion/Encaje_de_conectores_y_empalmes.json','Conectores_y_empalmes_15_motores.json'),(w/'Tendido_15_montaje_G8b_barrido_entrada_10.json','Cierre_P86_153_cables.json'),(w/'P86_782_solidos_barridos_exactos.json','Cierre_P86_solidos.json'),(w/'P86_prueba_de_rebaje.json','Cotas_del_rebaje_P86.json')):shutil.copyfile(f,v/to)
a=load(v/'Holguras_del_arnes_15_motores.json');e=load(v/'Electronica_ante_arnes_15_motores.json');con=load(v/'Conectores_y_empalmes_15_motores.json')
assert len(a['pares_de_aislamientos_solapados'])==29 and sum(map(len,e['interferencias_fuera_de_extremos'].values()))==31 and len(con)==24
assert all(not f['intersecciones_superiores_a_1e_6_mm3'] for f in load(v/'Cierre_P86_solidos.json'))
part=next((g/'STL_POR_COLORES').rglob('86_*.stl'));f=g/'Indice_STL_y_placas.csv';idx=rows(f);row=next(x for x in idx if x[0]=='P86');row[2]=str(part.relative_to(g));row[-1]=digest(part);wr(f,idx)
pl='AZUL_CIELO_PETG_0p2_R0_01';job=load(v/(pl+'.json'));ordp=rows(base/'Orden_de_impresion.csv');rw=next(x for x in ordp if x[0]==pl);rw[3]=f"{job['gramos']:.2f}";wr(g/'Orden_de_impresion.csv',ordp);gm=sum(float(x[3]) for x in ordp[1:]);blue=sum(float(x[3]) for x in ordp[1:] if x[0].startswith('AZUL_CIELO'))
mats=rows(base/'Lista_de_materiales.csv');mr=next(x for x in mats if x[0]=='AZUL_CIELO_PETG');mr[2]=f'{blue:.2f}';mr[3]=f'{math.ceil(blue*1.15)} g';wr(g/'Lista_de_materiales.csv',mats)
fn='Microduck_G9_arnes_y_montaje.blend'
guide="""# Cerrar la tapa P86 del Microduck V16 R1 G9

La cara inferior lleva tres alivios para los retornos de masa W106, W109 y W115. Se conservan los cuatro asientos de tornillo y el contorno superior. Para un robot que ya está impreso en G8 basta con sustituir P86 para probar esta maniobra. En el repuesto suelto, el proyecto imprime una pieza en PETG azul cielo, capa de 0,2 mm, con 11,38 g previstos y cero pausas. En la carpeta del robot, P86 comparte placa con nueve piezas y se conservan las pausas de esas piezas.

1. Deja el pack desconectado. Presenta primero el cassette y los conectores. Con la tapa fuera, lleva cada ramal a su recorrido según la escena 05. Comprueba que los cuatro apoyos de P86 estén limpios.
2. Mantén la tapa paralela a su asiento. Comienza 90 mm por detrás y 14 mm por encima. Avanza 72 mm a la misma altura. El eje +X de Blender apunta hacia la cabeza del robot en esta maniobra.
3. Avanza los 18 mm restantes mientras bajas 4 mm. La tapa queda alineada en planta y 10 mm por encima de su posición final. Desciende esos 10 mm en vertical. Si aparece resistencia, vuelve a sacar la tapa y localiza el cable o el conector que se mueve.
4. Con la tapa asentada coloca los cuatro M2 × 6 avellanados desde fuera, en el orden de la escena 04. Una tapa bien presentada apoya antes de apretar los tornillos. En Blender, los fotogramas 39, 75, 95 y 145 marcan los extremos de la trayectoria.

La comprobación compara P86 en movimiento con los 153 conductores nominales y 782 sólidos fijos, incluidos los 24 conectores o empalmes modelados. La prueba por volúmenes barridos da como mínimo 0,73 mm hasta las fundas en la aproximación y 0,66 mm en el descenso. Otra comprobación con paso más fino y subdivisión de cada traslación da 0,71 mm durante la maniobra completa. Las cifras son cotas inferiores en milímetros con redondeo hacia abajo. P86 hace contacto con su asiento en P44. La prueba de intersección volumétrica del asiento queda por debajo de 0,000001 mm³. En la posición final el cassette P45 y P83 quedan a 0,32 mm de la tapa.

El ensayo en CAD supone el cableado inmóvil en su recorrido nominal. La rigidez del mazo, las medidas del lote y el acabado de la impresión requieren presentación física. En el resto del robot persisten 29 pares de fundas solapadas, 31 avisos frente a electrónica o herrajes y contactos con algunos soportes impresos. Prueba de montaje con el pack desconectado.
"""
(g/'Montaje_de_P86.md').write_text(guide,'utf8');(rep/'LEEME.md').write_text(guide+'\nAbre el 3MF de Placas_P2S_AMS2 en Bambu Studio o utiliza el archivo de Para_la_P2S_laminado para la P2S de boquilla 0,4 mm.\n','utf8')
f=g/'Montaje_del_cassette.md';s=(base/f.name).read_text('utf8');a0=s.index('8. Presenta P86');b0=s.index('\n',a0);s=s[:a0]+'8. Cierra P86 con la aproximación a 14 mm, el descenso oblicuo y la bajada vertical final de 10 mm descritos en [Montaje de P86](Montaje_de_P86.md). La escena 04 reproduce la trayectoria hasta el cuarto tornillo.'+s[b0:];f.write_text(s,'utf8')
f=g/'LEEME.md';s=(base/f.name).read_text('utf8').replace('V16 R1 G8 · Ensayo de montaje','V16 R1 G9 · Ensayo de cierre').replace('Microduck_G8_arnes_y_montaje.blend',fn).replace('711.23 g',f'{gm:.2f} g').replace('El barrido nominal de la tapa conserva 0.154 mm en vertical y 0.154 mm en horizontal.','El barrido de la tapa conserva al menos 0,66 mm en el descenso final y 0,73 mm en la aproximación.').replace('Desde G7 cambian P14, P15, P34, P36, P38 y P66.','La G9 sustituye P86. Las otras 85 mallas corresponden a la G8.')
p=s.index('\n\n');s=s[:p]+'\n\n**Tapa P86.** La escena 04 muestra cómo cerrar la tapa con los 153 conductores completos. Consulta [Montaje de P86](Montaje_de_P86.md) para la secuencia y las holguras. La revisión de la tapa permite presentar el torso con el pack desconectado.'+s[p:];f.write_text(s,'utf8')
for n in ('Cierre_P86_153_cables','Cierre_P86_solidos','Cotas_del_rebaje_P86','Animacion_cierre_G9'):shutil.copyfile(v/(n+'.json'),rep/'Verificacion'/(n+'.json'))
for n in ('P86_aproximacion.png','P86_descenso.png','P86_atornillado.png'):shutil.copyfile(g/n,rep/n)
def pack(folder,target):
 files=sorted(p for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt');manifest=folder/'SHA256SUMS.txt';manifest.write_text(''.join(digest(p)+'  '+p.relative_to(folder).as_posix()+'\n' for p in files),'utf8');tmp=target.with_suffix('.assembling')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in [*files,manifest]:z.write(p,folder.name+'/'+p.relative_to(folder).as_posix())
 with zipfile.ZipFile(tmp) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
 tmp.replace(target)
pack(rep,r/'Microduck_G9_P86_repuesto_P2S.zip');pack(g,r/'Microduck_G9_P2S_ensayo_de_cierre.zip');print('PLACAS',len(ordp)-1,gm,flush=True)
