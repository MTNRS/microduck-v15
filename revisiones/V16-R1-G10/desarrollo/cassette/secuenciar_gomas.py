from recolocar import *
from scipy.ndimage import map_coordinates,gaussian_filter1d
from md9_routes import engine,ptr
from scipy.spatial.distance import cdist
from itertools import product
import time
m=int(sys.argv[1]);names=[f'OEM{m:02}-{i}' for i in (1,2,3)];mot=f'V7_SRC_V4_MD_{m:02}_MG90S_CUERPO';tips=np.array([wires[n]['closed'][-1] for n in names]);normal=unit(measure(mot,tips,.625)[1].mean(0)[None,:])[0];h=.30;low=tips.min(0)-15.;hi=tips.max(0)+15.;dim=np.ceil((hi-low)/h).astype(int)+1;F=np.full(dim,4.,'f');W=F.copy()
def idx(x):return np.clip(np.rint((x-low)/h).astype(int),0,dim-1)
def interp(a,p):return map_coordinates(a,((p-low)/h).T,order=1,mode='constant',cval=-3.)
keys=[k for k,(a,b) in {**rb,**wb}.items() if k not in names and np.all(a<hi+2)&np.all(b>low-2)]
for k in keys:
 a,b=(rb if k in rb else wb)[k];u=idx(a-4);v=idx(b+4)+1
 if np.any(u>=v):continue
 target=F if k in rb else W
 for z in range(u[2],v[2],6):
  l=u.copy();g=v.copy();l[2]=z;g[2]=min(z+6,g[2]);sl=tuple(slice(x,y) for x,y in zip(l,g));pt=low+h*(np.moveaxis(np.indices(g-l),0,-1)+l)
  ds=measure(k,pt.reshape(-1,3),.625)[0];np.minimum(target[sl],ds.reshape(g-l),out=target[sl])
allcurves={};origqs={n:dense(np.array(wires[n]['closed'])[::-1],.20) for n in names};stems={n:np.vstack([tips[i],tips[i]+normal*2.]) for i,n in enumerate(names)}
def borders(qs):
 a=qs.min(0)-2.;b=qs.max(0)+2.;return [k for k in keys if np.all(({**rb,**wb})[k][0]<b) and np.all(({**rb,**wb})[k][1]>a)]
def smooth_path(q,sm):
 s=arc(q);u=np.linspace(0,s[-1],int(s[-1]/.20)+2);p=np.column_stack([np.interp(u,s,v) for v in q.T]);res=gaussian_filter1d(p,sm,axis=0,mode='nearest');r=np.clip((u-1.2)/1.2,0,1)*np.clip((u[-1]-u)/1.0,0,1);return p+(res-p)*r[:,None]
def paths(n,slot,quick=False):
 qs=origqs[n];ar=arc(qs);tip=tips[slot];start=stems[n][-1];si=idx(start);candidates=[];sz=int(np.prod(dim));dest=np.empty(3000,'i')
 others=[origqs[k] for k in names if k!=n];qm=[];out={}
 for Aend in ((9.,15.,22.) if quick else (7.,10.,15.,19.,23.)):
  end_idx=np.searchsorted(ar,Aend);end=qs[end_idx];ei=idx(end)
  if not np.all((end>low+1)&(end<hi-1)):continue
  for margin in (.25,.12,.03):
   cost=1+np.maximum(0,.65-F)**2*4+np.maximum(0,.6-W)**2*4
   # A small bias towards the original exit tangent after the common parallel section.
   hard=(F<margin)|(W<margin);cost[hard]=1.e9
   if min(F[tuple(si)],W[tuple(si)],F[tuple(ei)],W[tuple(ei)])<margin:continue
   # Try both the factory ribbon alone and a route that avoids the incumbent paths of its neighbors.
   for side in ((0,) if quick else (0,1)):
    C=cost.copy()
    for k in names:
     if k==n:continue
     nearp=dense(stems[k],.13);samples=origqs[k][arc(origqs[k])<Aend+5] if side else []
     if len(samples):nearp=np.vstack((nearp,samples))
     t=cKDTree(nearp);l=idx(nearp.min(0)-2);g=idx(nearp.max(0)+2)+1;sl=tuple(slice(x,y) for x,y in zip(l,g));pt=low+h*(np.moveaxis(np.indices(g-l),0,-1)+l);dist=t.query(pt.reshape(-1,3))[0].reshape(g-l);C[sl]+=15*np.maximum(0,1.66-dist)**2
    C=np.ascontiguousarray(C,'f');dd=np.full(sz*2,1.e30,'f');pv=np.full(sz,-1,'i');heap=np.empty(sz,'i');ix=np.full(sz,-1,'i')
    ct=engine(ptr(C),*map(int,dim),int(np.ravel_multi_index(si,dim)),int(np.ravel_multi_index(ei,dim)),ptr(dest),len(dest),ptr(dd),ptr(pv),ptr(heap),ptr(ix))
    if ct<2:continue
    mid=low+h*np.column_stack(np.unravel_index(dest[:ct][::-1],dim));raw=np.vstack([tip,tip+normal*1.4,start,mid[1:-1],end,qs[min(end_idx+5,len(qs)-1)]])
    for sm in (7.,4.,2.5):
     pp=smooth_path(raw,sm);u=arc(pp);req=u>.95;mm=min(min(interp(F,pp[req])),min(interp(W,pp)))
     if mm<-.04:continue
     things=borders(pp);actual={}
     for k in things:
      q=pp[req] if k==mot else pp;actual[k]=float(min(measure(k,q,.625)[0]))
     mg=min(actual.values())
     if mg<.065:continue
     dirs=unit(np.diff(pp,axis=0));angles=np.arccos(np.clip(np.sum(dirs[:-1]*dirs[1:],axis=1),-1,1));steps=np.diff(u);rad=float(min(np.minimum(steps[1:],steps[:-1])/np.maximum(.00001,angles)));cut=min(end_idx+5,len(qs)-1)
     if rad<1.25:continue
     score=min(.5,mg)+.13*min(4,rad)-.01*arc(pp)[-1]
     candidates.append(dict(p=pp,cut=cut,q=np.vstack([pp,qs[cut+1:]]),score=score,mg=mg,radius=rad))
 print('motor',m,n,'trayectorias',len(candidates),flush=True);return candidates

from itertools import permutations
Wbase=W.copy()
def paintfield(F,p):
 parts=np.split(p,np.flatnonzero(np.linalg.norm(np.diff(p,axis=0),axis=1)>2.)+1)
 for pp in parts:
  pp=pp[np.all((pp>low-3)&(pp<hi+3),axis=1)]
  if not len(pp):continue
  for part in np.array_split(pp,max(1,len(pp)//50)):
   lo=idx(part.min(0)-2.7);up=idx(part.max(0)+2.7)+1;sl=tuple(slice(x,y) for x,y in zip(lo,up));grid=low+h*(np.moveaxis(np.indices(up-lo),0,-1)+lo);dist=cKDTree(part).query(grid.reshape(-1,3))[0]-1.25-.09;np.minimum(F[sl],dist.reshape(up-lo),out=F[sl])
 return F
def diversity(cs):
 keep=[]
 for c in sorted(cs,key=lambda u:-u['score']):
  p=c['p'];mid=np.array([p[np.searchsorted(arc(p),min(t,arc(p)[-1]))] for t in (3.,5.,7.)])
  if any(np.max(np.linalg.norm(mid-pt,axis=1))<.65 and abs(c['cut']-i)<13 for pt,i,_ in keep):continue
  keep.append((mid,c['cut'],c))
  if len(keep)>=3:break
 return [x[2] for x in keep]
def prepare(n,chosen):
 global W
 W=Wbase.copy()
 for y in names:
  if y==n:continue
  if y in chosen:paintfield(W,chosen[y]['q'])
  else:
   paintfield(W,dense(stems[y],.12));qs=origqs[y];paintfield(W,qs[arc(qs)>22.])
def compatible(n,c,fixed):
 p=c['p'];full=c['q'];tree=cKDTree(full);score=.4
 for k,v in fixed.items():
  score=min(score,min(cKDTree(v['q']).query(p)[0].min(),tree.query(v['p'])[0].min())-1.25-.105)
 return score
def finish(chosen):
 info={}
 for n,v in chosen.items():
  info[n]=dict(holgura_fija_mm=v['mg'],radio_minimo_aproximado_mm=v['radius'],nuevo_recorrido_hasta_union=v['p'].round(5).tolist(),union_desde_goma_mm=float(arc(origqs[n])[v['cut']]))
  full=v['q'][::-1].round(5).tolist();wires[n].update(closed=full,opened=full,longitud_trazada_mm=round(float(arc(np.array(full))[-1]),4))
 gaps={a+' / '+b:compatible(a,chosen[a],{b:chosen[b]}) for a,b in combinations(names,2)}
 save(dest/f'MG{m:02}_ramal_secuenciado.json',dict(cables=info,holguras_entre_fundas_mm=gaps));save(jdir/f'Tendido_G9_MG{m:02}_secuenciado.json',j);print('RESUELTO',m,gaps,flush=True)
def walk(order,i,chosen):
 if i==3:finish(chosen);return True
 n=order[i];prepare(n,chosen);cs=paths(n,names.index(n),True);cs=[x for x in cs if compatible(n,x,chosen)>.025]
 for c in diversity(cs):
  if walk(order,i+1,dict(chosen,**{n:c})):return True
 return False
for order in permutations(names):
 print('orden',order,flush=True)
 if walk(order,0,{}):break
