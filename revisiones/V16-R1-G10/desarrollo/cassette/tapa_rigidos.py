from pathlib import Path
import sys,tempfile
T=Path(tempfile.gettempdir());sys.path.insert(0,str(T))
from md15_rutas_locales import geos,readg,box,vec,near,tree,sd
import numpy as np,json
root=Path('microduck-v16').resolve();out=Path(__file__).parent;rig=dict(geos);lid=readg(T/'md8work/P86.npz')
for name in list(rig):
 if name=='P86' or name.startswith(('barrido_','F_M2x6_')):del rig[name]
for n in ('P44','P45','P83','P06','P65'):
 f=T/'microduck15print'/(n+'.npz')
 if f.exists():rig[n]=readg(f)
rig['P66']=readg(root/'trabajo/frontal_dos_pasos/JST_XH_balance/P66_con_salida_BM.npz')
j=json.loads((root/'V16_R1_G8_Ensayo_de_montaje/Tendido_15_motores_en_ensayo.json').read_text('utf8'))
for c in j['conectores']+j['empalmes']:
 if not c['id'].startswith('XT30'):
  u=np.asarray(c['center']);h=np.asarray(c['size'])/2;rig[c['id']]=box(u-h,u+h)
def pose(x,z):
 g=lid.translate([x,0,z]);res={}
 for n,h in near(g,rig,.015).items():
  if n in ('P86',):continue
  v=(g^h).volume()
  if v>.0001:res[n]=round(v,4)
 return res
if __name__=='__main__':
 report={}
 for h in (0,.25,1,2,4,6,8,10,12):
  poses=[0.] if h<6 else [0.,-4.,-8.,-15.,-28.,-45.,-72.,-90.]
  for x in poses:
   hits=pose(x,h);report[str((x,h))]=hits
   if hits:print('choque',x,h,hits,flush=True)
 (out/'P86_colision_rigida_por_posicion.json').write_text(json.dumps(report,indent=1),'utf8')
