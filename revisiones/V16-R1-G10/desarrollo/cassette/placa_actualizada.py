from pathlib import Path
import tempfile,shutil,json,sys,subprocess
T=Path(tempfile.gettempdir());r=Path('microduck-v16').resolve();old=r/'V16_R1_G8_Ensayo_de_montaje';g=r/'V16_R1_G9_Ensayo_de_cierre';ch=g/'Verificacion';env=T/'md19colorenv';env.mkdir(exist_ok=True)
def load(f):return json.loads(f.read_text('utf8'))
def save(f,a):f.write_text(json.dumps(a,indent=1,ensure_ascii=False),'utf8')
prep=load(ch/'Preparacion_STL.json')
for p in old.rglob('*'):
 rel=p.relative_to(old)
 if not p.is_file() or p.name in ('SHA256SUMS.txt','Microduck_G8_arnes_y_montaje.blend','86_Tapa_registro_curva.stl') or rel.as_posix()=='Verificacion/Preparacion_STL.json':continue
 (g/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,g/rel)
full=load(old/'Verificacion/Preparacion_STL.json');full['P86']=prep['P86'];save(ch/'Preparacion_STL.json',full)
plate='AZUL_CIELO_PETG_0p2_R0_01'
for p in (T/'md15env').glob('*.py'):
 s=p.read_text('utf-8-sig').replace("G=R/'V16_R1_G7'","G=R/'V16_R1_G9_Ensayo_de_cierre'").replace('microduck15print','md19colorwork')
 if p.name=='slice.py':
  i=s.index(' if file.stem not in ');k=s.index(':continue',i);s=s[:i]+f" if file.stem != '{plate}'"+s[k:]
 (env/p.name).write_text(s,'utf8')
(env/'preparar.py').write_text("from md9_batchfinal import *\nx=load(V/'AZUL_CIELO_PETG_0p2_R0_01.json');batch(x['piezas'],(x['color'],x['capas_mm'],x['raft']),'01')\nexec((Path(__file__).parent/'slice.py').read_text('utf8'))\n",'utf8')
for n in ('preparar.py','md9_delivery_audit.py'):subprocess.run([sys.executable,'-u',str(env/n)],check=True)
