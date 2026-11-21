from pathlib import Path
import tempfile,sys,json,math
T=Path(tempfile.gettempdir());sys.path[:0]=[str(T/'duck-r1-mechlib'),str(T/'md8lib'),str(T/'md7lib')]
import numpy as np, manifold3d as m,igl
M=m.Manifold;here=Path(__file__).parent;r=Path('microduck-v16');src=r/'trabajo/arnes_polaridad/arnes_15_motores/Tendido_G9_cierre.json'
def geom(fn):
 z=np.load(fn);return M(m.Mesh64(np.ascontiguousarray(z['v']),np.ascontiguousarray(z['f'],dtype='uint64')))
def verts(g):
 ms=g.to_mesh64();return np.asarray(ms.vert_properties)[:,:3].copy(),np.ascontiguousarray(ms.tri_verts,dtype='int64')
def saveg(n,g):
 v,f=verts(g);np.savez_compressed(here/(n+'.npz'),v=v,f=f)
def union(obs):return M.batch_boolean(obs,m.OpType.Add)
def box(l,h):return M.cube((np.asarray(h)-l).tolist()).translate(l)
def capsule(a,b,r):
 s=M.sphere(r,28);return M.batch_hull([s.translate(a),s.translate(b)])
def lengths(a):return np.r_[0,np.cumsum(np.linalg.norm(np.diff(a,axis=0),axis=1))]
def dense(a,step):
 return np.vstack([*[np.linspace(p,q,max(1,int(np.ceil(np.linalg.norm(q-p)/step))),endpoint=False) for p,q in zip(a,a[1:])],a[-1]])
def dist(g,p):
 v,f=verts(g);tree=igl.AABB();tree.init(v,f);d2,_,_=tree.squared_distance(v,f,p);ds=np.sqrt(d2);ii=ds<3
 ds[ii]*=np.where(abs(igl.fast_winding_number(v,f,p[ii]))>.5,-1,1);return ds
lid=geom(T/'md8work/P86.npz');ws={w['id']:w for w in json.loads(src.read_text('utf8'))['hilos']}
def relief():
 cs=[];checks={}
 for n in ('W106','W109','W115'):
  w=ws[n];rr=w['od']/2;a=np.array(w['closed']);p=dense(a,.20);sel=np.flatnonzero(np.all((p>[-11,-14,154])&(p<[1.,6.,159.]),axis=1))
  close=sel[dist(lid,p[sel])<rr+1.36];idx=np.unique(np.clip(np.concatenate([close+o for o in (-1,0,1)]),0,len(p)-1))
  for chunk in np.split(idx,np.flatnonzero(np.diff(idx)>1)+1):
   if len(chunk)<2:continue
   sub=p[chunk];knots=[0];s=lengths(sub)
   for i in range(1,len(chunk)-1):
    if s[i]-s[knots[-1]]>.39:knots.append(i)
   knots.append(len(sub)-1);q=sub[knots]
   cs.extend(capsule(a,b,rr+1.04) for a,b in zip(q,q[1:]))
  checks[n]=round(float(min(dist(lid,p[sel]))-rr-.1),4)
 cutter=union(cs)^box([-11,-14,150],[1.0,6,159.72]);g=lid-cutter
 removed=lid^cutter;saveg('P86_alivio_interior',g);saveg('P86_material_retirado',removed);v,f=verts(removed);stockv,_=verts(lid)
 info=dict(volumen_inicial_mm3=lid.volume(),volumen_retirado_mm3=removed.volume(),cierre_un_solo_solido=[c.volume() for c in g.decompose()],limites_del_corte=[v.min(0).tolist(),v.max(0).tolist()],margenes_antes=checks)
 for n in checks:
  p=dense(np.array(ws[n]['closed']),.12);info.setdefault('margenes_despues_estado_cerrado',{})[n]=round(float(min(dist(g,p))-ws[n]['od']/2-.06),4)
 ax=json.loads((T/'md8work/axes.json').read_text())
 info['holgura_material_retirado_a_tornillos_mm']={n:round(removed.min_gap(geom(T/'md8work'/(n+'.npz')),30),4) for n in ax}
 # Sample the complete affected XY footprint, retaining the solid column above each cut.
 lo=v.min(0);hi=v.max(0);thicks=[];outer=[];change=0
 for x in np.arange(lo[0]+.02,hi[0],.10):
  for y in np.arange(lo[1]+.02,hi[1],.10):
   hits=removed.ray_cast((x,y,151),(x,y,180))
   if not hits:continue
   tops=[c.position[2] for c in lid.ray_cast((x,y,151),(x,y,180))];ends=[c.position[2] for c in g.ray_cast((x,y,151),(x,y,180))];cut=hits[-1].position[2]
   if not tops or not ends:continue
   change=max(change,abs(tops[-1]-ends[-1]));outer.append(tops[-1]-cut)
   for bot,top in zip(ends[::2],ends[1::2]):
    if abs(bot-cut)<.002:thicks.append(top-bot);break
 info.update(espesor_en_columnas_afectadas_min_mm=min(thicks),profundidad_min_bajo_piel_superior_mm=min(outer),cambio_maximo_perfil_superior_mm=change,muestras_de_columnas=len(thicks))
 (here/'P86_prueba_de_rebaje.json').write_text(json.dumps(info,indent=1),'utf8');print(info,flush=True)
if __name__=='__main__':relief()
