from pathlib import Path
import json,tempfile,subprocess,sys
T=Path(tempfile.gettempdir());root=Path('microduck-v16').resolve();g=root/'V16_R1_G10_Ensayo_P45';env=T/'md20p45env';env.mkdir(exist_ok=True);v=g/'Verificacion';(v/'Trabajos_laminados.json').write_text('{}','utf8')
for f in ('md9_batchfinal.py','md9_common.py','md9_delivery_audit.py','slice.py'):
 s=(T/'md19soloen'/f).read_text('utf8').replace('V16_R1_G9_Reposicion_P86','V16_R1_G10_Ensayo_P45').replace('md19solowork','md20p45work').replace('AZUL_CIELO_PETG_0p2_R0_P86','AZUL_CIELO_PETG_0p1_R3_P45')
 (env/f).write_text(s,'utf8')
(env/'solo.py').write_text("from md9_batchfinal import *\nbatch(['P45'],('AZUL_CIELO_PETG','0.1','3'),'P45');exec((Path(__file__).parent/'slice.py').read_text('utf8'))\n",'utf8')
for f in ('solo.py','md9_delivery_audit.py'):subprocess.run([sys.executable,'-u',str(env/f)],check=True)
