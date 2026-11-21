from pathlib import Path
import json,shutil,tempfile,sys,subprocess
r=Path('microduck-v16').resolve();h=r/'trabajo/cierre_G9';k=r/'V16_R1_G10_Ensayo_P45';g=r/'V16_R1_G10_Ensayo_de_cassette';old=r/'V16_R1_G9_Ensayo_de_cierre';v=g/'Verificacion';T=Path(tempfile.gettempdir());g.mkdir(exist_ok=True)
for p in old.rglob('*'):
 if not p.is_file() or p.name in ('SHA256SUMS.txt','Microduck_G9_arnes_y_montaje.blend') or (p.suffix=='.stl' and p.name.startswith('45_')):continue
 dst=g/p.relative_to(old);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
def rd(f):return json.loads(f.read_text('utf-8-sig'))
def wr(f,j):f.write_text(json.dumps(j,indent=1,ensure_ascii=False),'utf8')
f=next((k/'STL_POR_COLORES').rglob('45_*.stl'));shutil.copyfile(f,g/f.relative_to(k));prep=rd(v/'Preparacion_STL.json');prep.update(rd(k/'Verificacion/Preparacion_STL.json'));wr(v/'Preparacion_STL.json',prep)
for n in ('Geometria_del_canal_BM.json','Superficie_exterior_y_apoyos_de_P45.json'):shutil.copyfile(k/'Verificacion'/n,v/n)
env=T/'md20full';env.mkdir(exist_ok=True)
plate='AZUL_CIELO_PETG_0p1_R3_COMPACTA'
for n in ('md9_common','md9_batchfinal','slice','md9_delivery_audit'):
 f=T/'md19colorenv'/(n+'.py');s=f.read_text('utf8').replace('V16_R1_G9_Ensayo_de_cierre',g.name).replace('md19colorwork','md20fullwork')
 if n=='slice':s=s.replace('AZUL_CIELO_PETG_0p2_R0_01',plate)
 (env/f.name).write_text(s,'utf8')
(env/'do.py').write_text("from md9_batchfinal import *\nx=load(V/'AZUL_CIELO_PETG_0p1_R3_COMPACTA.json');batch(x['piezas'],(x['color'],x['capas_mm'],x['raft']),'COMPACTA');exec((Path(__file__).parent/'slice.py').read_text('utf8'))\n",'utf8')
for f in ('do.py','md9_delivery_audit.py'):subprocess.run([sys.executable,'-u',str(env/f)],check=True)
