from pathlib import Path
import tempfile,shutil,json,subprocess,sys
T=Path(tempfile.gettempdir());r=Path('microduck-v16').resolve();G=r/'V16_R1_G9_Ensayo_de_cierre';S=r/'V16_R1_G9_Reposicion_P86';V=S/'Verificacion';V.mkdir(parents=True,exist_ok=True);f=next((G/'STL_POR_COLORES').rglob('86_*.stl'));dest=S/'STL_POR_COLORES'/f.parent.name;dest.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest/f.name)
prep=json.loads((G/'Verificacion/Preparacion_STL.json').read_text('utf8'));(V/'Preparacion_STL.json').write_text(json.dumps({'P86':prep['P86']},indent=1),'utf8');(V/'Trabajos_laminados.json').write_text('{}','utf8')
env=T/'md19soloen';env.mkdir(exist_ok=True)
for f in (T/'md19colorenv').glob('*.py'):
 s=f.read_text('utf8').replace('V16_R1_G9_Ensayo_de_cierre','V16_R1_G9_Reposicion_P86').replace('md19colorwork','md19solowork').replace('len(out)==9 and len(visited)==86','len(out)==1 and len(visited)==1')
 if f.name=='slice.py':s=s.replace('AZUL_CIELO_PETG_0p2_R0_01','AZUL_CIELO_PETG_0p2_R0_P86')
 (env/f.name).write_text(s,'utf8')
(env/'solo.py').write_text("from md9_batchfinal import *\nbatch(['P86'],('AZUL_CIELO_PETG','0.2','0'),'P86');exec((Path(__file__).parent/'slice.py').read_text('utf8'))\n",'utf8')
for n in ('solo.py','md9_delivery_audit.py'):subprocess.run([sys.executable,'-u',str(env/n)],check=True)
