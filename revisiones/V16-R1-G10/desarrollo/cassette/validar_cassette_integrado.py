from pathlib import Path
import json,tempfile,subprocess,sys,os
p=Path('microduck-v16/trabajo/arnes_polaridad/arnes_15_motores')
def read(n):return json.loads((p/(n+'.json')).read_text('utf8'))
j=read('Tendido_G9_ramal14_y_pares');base={w['id']:w for w in read('Tendido_15_montaje_G8b')['hilos']};bm=next(w for w in read('Tendido_G9_BM_borde')['hilos'] if w['id']=='W003')
j['hilos']=[base[w['id']] if w['id'] in ('W090','W091','OEM09-3') else bm if w['id']=='W003' else w for w in j['hilos']]
tag='Tendido_G10_cassette';(p/(tag+'.json')).write_text(json.dumps(j,indent=1,ensure_ascii=False),'utf8')
os.environ['MD16_CHECK']=tag;T=Path(tempfile.gettempdir());e=T/'md20aud';e.mkdir(exist_ok=True)
for f in (T/'md19audit').glob('*.py'):
 s=f.read_text('utf8')
 if f.name=='electronics.py':s=s.replace("for key,file in {'P86':","for key,file in {'P45':'P45_BM_canal_sin_isla','P86':")
 if f.name=='wires.py':s=s.replace("fix={'P86':","fix={'P45':'P45_BM_canal_sin_isla','P86':")
 (e/f.name).write_text(s,'utf8')
jobs=[subprocess.Popen([sys.executable,'-u',str(e/(name+'.py'))]) for name in ('wires','electronics')]
assert all(job.wait()==0 for job in jobs)
