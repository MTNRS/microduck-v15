"""Build a channel for the BM lead over the actual cassette insertion stroke."""
from prisma import *
from scipy.spatial import cKDTree
from pathlib import Path
import trimesh,itertools,hashlib
raw=geom(T/'microduck15print/P45.npz')
reference=next((r/'V16_R1_G9_Ensayo_de_cierre/STL_POR_COLORES').rglob('45_*.stl'))
stl=trimesh.load(reference,force='mesh');vv,ff=verts(raw);sx=cKDTree(stl.vertices)
def mid(v):return (np.min(v,axis=0)+np.max(v,axis=0))/2
def align():
 options=[]
 for axes in itertools.permutations(range(3)):
  for signs in itertools.product((-1,1),repeat=3):
   a=np.eye(3)[list(axes)]*np.asarray(signs)[:,None]
   if np.linalg.det(a)<.99:continue
   b=mid(stl.vertices)-a@mid(vv);q=vv@a.T+b;err=sx.query(q[::max(1,len(q)//320)])[0].max();options.append((err,a,b))
 _,a,b=min(options,key=lambda z:z[0]);q=vv@a.T+b
 err=max(sx.query(q)[0].max(),cKDTree(q).query(stl.vertices)[0].max());return a,b,err
def simplify(q):
 if len(q)<3:return q
 u=q[-1]-q[0];d=q-q[0];proj=np.clip(d@u/(u@u),0,1);dist=np.linalg.norm(d-proj[:,None]*u,axis=1);i=dist.argmax()
 if dist[i]<=.026:return q[[0,-1]]
 return np.vstack((simplify(q[:i+1])[:-1],simplify(q[i:])))
def mk(q,radius,jumps):
 sphere=M.sphere(radius,32);objects=[] 
 for a,b in zip(q,q[1:]):
  for x,y in zip(jumps,jumps[1:]):
   pts=[a+x,b+x,a+y,b+y];objects.append(M.batch_hull([sphere.translate(p.tolist()) for p in pts]))
 return union(objects)
def run():
 a,b,e=align();print('registro STL',e,flush=True);assert e<.005,(a,b,e)
 info=json.loads((here/'BM_desvio_junto_al_pad.json').read_text('utf8'));q=np.asarray(info['tramo']);stroke=np.array([[0,0,0],[0,4,-1],[0,28,-62]])
 nodes=simplify(q);tool=mk(nodes,1.10,stroke);removed=raw^tool;new=raw-tool;travel=mk(q,.55,stroke);zone=verts(removed)[0];pieces=[float(x.volume()) for x in new.decompose() if abs(x.volume())>1.e-5]
 details=dict(registro_con_stl_publicado_mm=float(e),volumen_original_mm3=raw.volume(),retirado_mm3=removed.volume(),extremos_del_rebaje_mm=[zone.min(0).tolist(),zone.max(0).tolist()],cuerpos_con_volumen=pieces,estado=str(new.status()),barrido_cable_con_cassette_anterior_mm3=(travel^raw).volume(),barrido_cable_con_cassette_corregido_mm3=(travel^new).volume(),holgura_barrido_cassette_mm=travel.min_gap(new,3),trayectoria_relativa_mm=stroke.tolist(),ejes_para_stl=a.tolist(),traslacion_para_stl=b.tolist())
 print(details,flush=True)
 saveg('P45_BM_rebaje_de_prueba',new);saveg('P45_BM_material_retirado',removed);saveg('BM_barrido_de_entrada',travel)
 (here/'P45_BM_rebaje_de_prueba.json').write_text(json.dumps(details,indent=1),'utf8')
if __name__=='__main__':run()
