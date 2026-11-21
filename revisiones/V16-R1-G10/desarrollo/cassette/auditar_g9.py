from pathlib import Path
import tempfile,subprocess,sys,shutil,os
T=Path(tempfile.gettempdir());env=T/'md19audit';env.mkdir(exist_ok=True);r=Path('microduck-v16').resolve();work=r/'trabajo/cierre_G9';j=r/'trabajo/arnes_polaridad/arnes_15_motores';tag=os.environ.get('MD16_CHECK','Tendido_G9_tapa_comprobada');os.environ['MD16_CHECK']=tag
if tag=='Tendido_G9_tapa_comprobada':shutil.copyfile(j/'Tendido_15_montaje_G8b.json',j/(tag+'.json'))
for p in (T/'md17audbm').glob('*.py'):
 s=p.read_text('utf-8-sig')
 if p.name=='wires.py':
  s=s.replace("d=np.load(rawroot/", "fix={'P86':'P86_alivio_interior','barrido_vertical':'barrido_bajada_G9','barrido_horizontal':'barrido_entrada_G9'};d=np.load(rawroot/'trabajo/cierre_G9'/(fix[n]+'.npz') if n in fix else rawroot/")
 if p.name=='electronics.py':
  pos=s.index('for c in con:')
  s=s[:pos]+"""for key,file in {'P86':'P86_alivio_interior','barrido_vertical':'barrido_bajada_G9','barrido_horizontal':'barrido_entrada_G9'}.items():allg[key]=readg(G.parent/'trabajo/cierre_G9'/(file+'.npz'))
bds={k:vec(g) for k,g in allg.items()}
"""+s[pos:]
 (env/p.name).write_text(s,'utf8')
procs=[subprocess.Popen([sys.executable,'-u',str(env/(n+'.py'))]) for n in ('wires','electronics')]
assert all(p.wait()==0 for p in procs)
