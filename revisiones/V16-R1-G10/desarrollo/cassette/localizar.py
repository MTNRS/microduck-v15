from pathlib import Path
import json,sys,tempfile
import numpy as np
T=Path(tempfile.gettempdir())
sys.path[:0]=[str(T/'md8lib'),str(T/'md7lib'),str(T/'md17audbm'),str(T)]
import igl
from perfil_terminales import sampled_profile
r=Path('microduck-v16');base=r/'trabajo/arnes_polaridad/arnes_15_motores';src=base/(sys.argv[1]+'.json')
h=json.loads(src.read_text('utf8'));dest=Path(__file__).parent
wires={w['id']:sampled_profile(w,.12) for w in h['hilos']}
for n in ('barrido_vertical','barrido_horizontal','P86','P44','P45','P83'):
 fn=(T/'md8work'/(n+'.npz'))
 if n.startswith('P'):
  f=T/'microduck15print'/(n+'.npz')
  if f.exists():fn=f
 if not fn.exists():continue
 z=np.load(fn);v=z['v'];f=z['f'].astype('int64');tr=igl.AABB();tr.init(v,f);out=[]
 for key,(p,rad) in wires.items():
  idx=np.flatnonzero(np.all((p>v.min(0)-4)&(p<v.max(0)+4),axis=1))
  if not len(idx):continue
  q=p[idx];s,fi,closest=tr.squared_distance(v,f,q);ds=np.sqrt(s);near=ds<4.;ds[near]*=np.where(abs(igl.fast_winding_number(v,f,q[near]))>.5,-1.,1.);ds-=rad[idx]+.06
  i=int(np.argmin(ds))
  if ds[i]<1.1:out.append(dict(hilo=key,mm=round(float(ds[i]),4),cable=q[i].round(4).tolist(),superficie=closest[i].round(4).tolist(),desde_extremo=round(float(min(np.linalg.norm(q[i]-p[0]),np.linalg.norm(q[i]-p[-1]))),3)))
 out.sort(key=lambda x:x['mm']);(dest/(sys.argv[1]+'_'+n+'.json')).write_text(json.dumps(out,indent=1),'utf8')
 print(n,[(a['hilo'],a['mm'],a['desde_extremo']) for a in out[:9]],flush=True)
