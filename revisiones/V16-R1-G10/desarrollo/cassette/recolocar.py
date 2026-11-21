"""Local wire moves constrained by actual part surfaces and the rest of the fitted harness. World frame, mm."""
import os,sys,tempfile
from pathlib import Path
T=Path(tempfile.gettempdir());sys.path.insert(0,str(T))
from md15_rutas_locales import geos,readg,box,tree,vec,sskin,sd
import numpy as np, json
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from scipy.interpolate import CubicSpline
from itertools import combinations
root=Path('microduck-v16').resolve();jdir=root/'trabajo/arnes_polaridad/arnes_15_motores'
dest=Path(__file__).parent
def load(f):return json.loads(f.read_text('utf8'))
def save(f,j):f.write_text(json.dumps(j,indent=1,ensure_ascii=False),'utf8')
base='Tendido_15_montaje_G8b';tag=os.environ.get('MD_G9_TAG','Tendido_G9_cierre')
j=load(jdir/((tag if (jdir/(tag+'.json')).exists() else base)+'.json'))
wires={w['id']:w for w in j['hilos']};geom=dict(geos)
for k in ('barrido_horizontal','barrido_vertical','P86'):geom[k]=readg(T/'md8work'/(k+'.npz'))
for k in ('P44','P45','P83','P06','P65'):
 f=T/'microduck15print'/(k+'.npz')
 if f.exists():geom[k]=readg(f)
geom['P66']=readg(root/'trabajo/frontal_dos_pasos/JST_XH_balance/P66_con_salida_BM.npz')
geom['V7_Y_POWER_HOUSING_14']=readg(jdir.parent/'Harwin_P14_2_contactos.npz')
for c in j['conectores']+j['empalmes']:
 if not c['id'].startswith('XT30'):
  pt=np.array(c['center']);ext=np.array(c['size'])/2;geom[c['id']]=box(pt-ext,pt+ext)
for k in ('P14','P15'):geom[k]=readg(root/'trabajo/frontal_dos_pasos/pasos_en_brazos/ventanas_de_servicio'/(k+'_entrada_a_mano.npz'))
for k in ('P34','P36','P38'):geom[k]=readg(root/'trabajo/mandibula/movil_G8'/(k+'.npz'))
def dense(q,h):
 q=np.asarray(q);return np.vstack([*[np.linspace(a,b,max(1,int(np.ceil(np.linalg.norm(a-b)/h))),endpoint=False) for a,b in zip(q,q[1:])],q[-1]])
def arc(q):return np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))]
def unit(q):return q/np.maximum(np.linalg.norm(q,axis=-1,keepdims=True),1.e-9)
import igl
rb={k:vec(g) for k,g in geom.items()};cache={};wb={};wt={}
def setup(n):
 q=dense(wires[n]['closed'],.14);wt[n]=cKDTree(q);wb[n]=(q.min(0),q.max(0))
for n in wires:setup(n)
def measure(k,p,r):
 if k in wt:
  d,i=wt[k].query(p);return d-wires[k]['od']/2-r-.08,unit(p-wt[k].data[i])
 if k not in cache:cache[k]=tree(geom[k])
 v,f,t=cache[k];ds,fi,pt=t.squared_distance(v,f,p);d=np.sqrt(ds);sg=np.ones(len(d));ix=d<4.
 if ix.any():sg[ix]=np.where(abs(igl.fast_winding_number(v,f,p[ix]))>.5,-1.,1.)
 return d*sg-r-.08,unit(p-pt)*sg[:,None]
def attempt(n,target,point,goal,radius):
 w=wires[n];orig=np.array(w['closed']);assert np.array_equal(orig,w['opened']);full=dense(orig,.25);ar=arc(full);cen=np.argmin(np.linalg.norm(full-point,axis=1));lim=(ar[max(0,cen)]-radius,ar[cen]+radius);ii=np.flatnonzero((ar>max(lim[0],1.25))&(ar<min(lim[1],ar[-1]-1.25)));p=full[ii];s=ar[ii];L=s[-1]-s[0];print('tramo',n,target,round(L,2),flush=True)
 if L<2.4:return
 r=w['od']/2;low=p.min(0)-3.7;hi=p.max(0)+3.7
 keys=[k for k,(lo,up) in {**rb,**wb}.items() if k!=n and np.all(lo<hi)&np.all(up>low)]
 keys=list(dict.fromkeys(keys+[target]))
 anchors=np.linspace(s[0],s[-1],max(5,min(10,int(L/2.5)+2)));B=CubicSpline(anchors,np.eye(len(anchors)),axis=0,bc_type='clamped')(s)[:,1:-1];nc=B.shape[1]
 baseline={k:measure(k,p,r)[0] for k in keys};keys=[k for k in keys if min(baseline[k])<2.4 or k==target]
 # Pin protected transitions, minimise changes away from the defect and prevent any newly negative clearances.
 thresholds={k:np.minimum(baseline[k]-.012,.38) for k in keys};thresholds[target]=np.full(len(p),goal)
 # Distances to other already-interfering items may improve but must not get worse.
 old=baseline[target].min();coef=np.zeros((nc,3));basis=B;out=p.copy();D2=np.diff(np.eye(nc+2),n=2,axis=0)[:,1:-1];reg=np.eye(nc)*.05+D2.T@D2*.13
 for iteration in range(16):
  vv=[];jj=[];weights=[]
  for k in keys:
   v,g=measure(k,out,r);dif=thresholds[k]-v;mask=dif>-.65
   if not mask.any():continue
   vv.extend(dif[mask]);jj.extend((basis[mask,:,None]*g[mask,None,:]).reshape(mask.sum(),-1));weights.extend([3. if k==target else 55.]*mask.sum())
  if not vv:break
  A=np.asarray(jj);err=np.array(vv);wt0=np.array(weights)
  def cost(x):
   cf=coef+x.reshape(nc,3);pen=np.maximum(err-A@x,0);return float((wt0*pen)@pen+(cf*(reg@cf)).sum()+.04*(x@x)), -2*A.T@(wt0*pen)+2*(reg@cf).ravel()+.08*x
  res=minimize(cost,np.zeros(nc*3),jac=True,method='L-BFGS-B',bounds=[(-.28,.28)]*(nc*3),options={'maxiter':80,'ftol':1e-10})
  step=res.x.reshape(nc,3);coef+=step;out=p+B@coef
  if np.max(abs(step))<.006:break
 # Backtrack the whole shape against exact distances. The limiting neighbor can later move independently.
 initial=out.copy()
 for frac in (1.,.88,.76,.64,.52,.40,.28,.17):
  out=p+(initial-p)*frac
  if all(np.max(np.minimum(baseline[k],.32)-measure(k,out,r)[0])<.028 for k in keys if k!=target):break
 after={k:measure(k,out,r)[0] for k in keys};new=after[target].min()
 losers={k:round(float((np.minimum(baseline[k],.32)-after[k]).max()),3) for k in keys if k!=target and np.max(np.minimum(baseline[k],.32)-after[k])>.03}
 skin=(p[:,2]>120)&(p[:,2]<167)
 if skin.any():
  a=sd(sskin,p[skin]);b=sd(sskin,out[skin]);bad=(a<-.25)&(b>np.maximum(-.2,a+.5))
  if bad.any():losers['exterior']=float(b[bad].max())
 print('resultado',round(float(old),3),round(float(new),3),losers,flush=True)
 if new<old+.035 or losers:return
 full[ii]=out
 # Keep the original unsampled corners and the untouched portions of the original wire intact.
 oo=arc(orig);keep0=orig[oo<s[0]-1.e-6];keep1=orig[oo>s[-1]+1.e-6];q=np.vstack((keep0,out,keep1))
 w.update(closed=q.round(6).tolist(),opened=q.round(6).tolist(),longitud_trazada_mm=round(float(arc(q)[-1]),4));setup(n)
 save(jdir/(tag+'.json'),j);fp=dest/(tag+'_cambios.json');hist=load(fp) if fp.exists() else [];hist.append(dict(hilo=n,obstaculo=target,intervalo_desde_origen_mm=s[[0,-1]].tolist(),antes=float(old),despues=float(new),desplazamiento_maximo_mm=float(np.linalg.norm(out-p,axis=1).max())));save(fp,hist)
if __name__=='__main__':
 for spec in sys.argv[1:]:
  n,k,goal,radius=spec.split(':');a=next(r for r in load(dest/(base+'_'+k+'.json')) if r['hilo']==n);attempt(n,k,np.array(a['cable']),float(goal),float(radius))
