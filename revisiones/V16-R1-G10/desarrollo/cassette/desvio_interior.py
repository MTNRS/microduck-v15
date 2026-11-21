from recolocar import *
from md9_routes import engine,ptr
from scipy.ndimage import gaussian_filter1d
from collections import Counter

for key,file in {'P86':'P86_alivio_interior','barrido_vertical':'barrido_bajada_G9','barrido_horizontal':'barrido_entrada_G9'}.items():
 geom[key]=readg(dest/(file+'.npz'));rb[key]=vec(geom[key]);cache.pop(key,None)
name=sys.argv[1];wire=wires[name];r=wire['od']/2
static={**rb,**wb};del static[name]
def limits(p,margin):
 low=p.min(0)-margin;high=p.max(0)+margin
 return [k for k,(a,b) in static.items() if np.all(b>=low) and np.all(a<=high)]
def curve_gaps(p):
 return {k:float(np.min(measure(k,p,r)[0])) for k in limits(p,r+2.2)}
def samples(q,gap):
 s=arc(q);u=np.linspace(0,s[-1],int(np.ceil(s[-1]/gap))+1)
 return np.stack([np.interp(u,s,x) for x in q.T],axis=1)
def round_path(q,i0,i1,old,sigma):
 left=max(0,i0-15);right=min(len(old)-1,i1+15)
 ext=np.vstack((old[left:i0],q,old[i1+1:right+1]))
 p=samples(ext,.16);s=arc(p);sm=gaussian_filter1d(p,sigma,axis=0,mode='nearest')
 weight=np.clip(s/2,0,1)*np.clip((s[-1]-s)/2,0,1)
 weight=weight*weight*(3.-2.*weight)
 return p+(sm-p)*weight[:,None],left,right
def install(parts,s0,s1,new):
 w=wire;ss=arc(parts);curve=np.vstack((parts[ss<s0-1.e-6],new,parts[ss>s1+1.e-6]))
 assert np.allclose(curve[[0,-1]],parts[[0,-1]])
 w['closed']=curve.round(6).tolist();w['opened']=w['closed'];w['longitud_trazada_mm']=round(arc(curve)[-1],3);setup(name)
def route(pt,boxhalf):
 coords=np.array(pt,float);dim=np.ceil(np.array(boxhalf)*2/step).astype(int)+1;low=coords-(dim-1)*step/2;sz=int(np.prod(dim));grid=np.full(tuple(dim),4.,'f');domain=np.array([low,low+(dim-1)*step])
 print('campo',name,pt,sz,flush=True)
 def idx(x):return np.clip(np.rint((x-low)/step).astype(int),0,dim-1)
 for k in limits(domain,r+2.5):
  a,b=static[k];a=idx(a-r-2.8);b=idx(b+r+2.8)+1
  for z in range(a[2],b[2],5):
   lo=a.copy();hi=b.copy();lo[2]=z;hi[2]=min(z+5,b[2]);sl=tuple(slice(l,h) for l,h in zip(lo,hi));pts=low+step*(np.moveaxis(np.indices(hi-lo),0,-1)+lo);ds=measure(k,pts.reshape(-1,3),r)[0];np.minimum(grid[sl],ds.reshape(tuple(hi-lo)),out=grid[sl])
 # Check the complete insulation remains within the approved torso exterior.
 for z in range(0,dim[2],4):
  hi=min(z+4,dim[2]);sl=(slice(None),slice(None),slice(z,hi));p=low+step*(np.moveaxis(np.indices(grid[sl].shape),0,-1)+[0,0,z]);ds=-sd(sskin,p.reshape(-1,3))-r-.08;np.minimum(grid[sl],ds.reshape(grid[sl].shape),out=grid[sl])
 orig=np.array(wire['closed']);old=samples(orig,.32);s=np.linspace(0,arc(orig)[-1],len(old));nearest=np.argmin(np.linalg.norm(old-coords,axis=1));gi=grid[tuple(idx(old).T)];inside=np.all((old>domain[0]+.65)&(old<domain[1]-.65),axis=1)
 # Try both a short deviation and a shortcut between separate traversals of this compartment.
 ls=[i for i in range(1,nearest-3,3) if inside[i] and gi[i]>.12 and s[nearest]-s[i]>3]
 rs=[i for i in range(nearest+4,len(old)-1,3) if inside[i] and gi[i]>.12 and s[i]-s[nearest]>3]
 print('anclajes',len(ls),len(rs),'piel en centro',sd(sskin,coords.reshape(1,3)),flush=True)
 def candidates():
  for i in ls:
   for k in rs:
    score=(s[k]-s[i])-np.linalg.norm(old[i]-old[k])
    yield score,i,k
 ranks=sorted(candidates(),reverse=True)
 seen=set();pairs=[]
 for _,i,k in ranks:
  unique=(int(s[i]/3),int(s[k]/3))
  if unique not in seen:pairs.append((i,k));seen.add(unique)
 if not pairs:return
 failures=Counter()
 for margin in (.38,.21,.09):
  cf=1+3*np.maximum(0,1.0-grid)**2;cf[grid<margin]=1.e9;cf=np.ascontiguousarray(cf,'f');buf=np.empty(5000,'i');dd=np.empty(sz*2,'f');pv=np.empty(sz,'i');heap=pv.copy();ix=pv.copy()
  for i,k in pairs[:180]:
   ai=np.ravel_multi_index(idx(old[i]),dim);bi=np.ravel_multi_index(idx(old[k]),dim)
   if max(cf.flat[ai],cf.flat[bi])>1e8:continue
   dd.fill(1e30);pv.fill(-1);ix.fill(-1)
   ct=engine(ptr(cf),*map(int,dim),int(ai),int(bi),ptr(buf),len(buf),ptr(dd),ptr(pv),ptr(heap),ptr(ix))
   if ct<2:
    failures['sin_conexion']+=1;continue
   raw=np.vstack((old[i],low+step*np.column_stack(np.unravel_index(buf[:ct][::-1],dim))[1:-1],old[k]))
   for sigma in (8.,5.,3.):
    trial,ii,kk=round_path(raw,i,k,old,sigma);p=samples(trial,.12)
    if max(sd(sskin,p))+r+.06>-.10:
     failures['forma_exterior']+=1;continue
    gaps=curve_gaps(p);mg=min(gaps.values())
    if mg<.12:
     failures[min(gaps,key=gaps.get)]+=1;continue
    outside=np.vstack((old[:max(0,ii-16)],old[kk+17:]))
    if len(outside) and cKDTree(outside).query(p)[0].min()<2*r+.18:
     failures['propio_recorrido']+=1;continue
    sp=samples(np.vstack((old[max(0,ii-3):ii],trial,old[kk+1:kk+4])),.4);dv=unit(np.diff(sp,axis=0));angle=np.arccos(np.clip(np.sum(dv[:-1]*dv[1:],axis=1),-1,1));rad=float(min(np.linalg.norm(np.diff(sp,axis=0),axis=1)[1:]/np.maximum(angle,1e-6)))
    if rad<1.5:
     failures['curvatura']+=1;continue
    hist.append(dict(hilo=name,centro=pt,antes_mm=round(s[kk]-s[ii],3),despues_mm=round(arc(trial)[-1],3),holgura_minima_mm=round(mg,4),radio_aproximado_mm=round(rad,3),vecinos={n:round(v,4) for n,v in gaps.items() if v<1.1}))
    print('aceptado',hist[-1],flush=True);install(orig,s[ii],s[kk],trial)
    save(dest/(tag+'_desvios.json'),hist);save(jdir/(tag+'.json'),j);return
 print('sin ruta',name,pt,failures.most_common(8),flush=True)
hist=[];step=.44
for spec in sys.argv[2:]:
 v=list(map(float,spec.split(',')));route(v[:3],v[3:])
