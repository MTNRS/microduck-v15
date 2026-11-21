from rebaje_tapa import *
import time
def sweep_exact(g,d):
 v,f=verts(g);tri=v[f];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);face=np.asarray([[2,1,0],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]],dtype='uint64');dp=np.array(d,float)
 use=np.flatnonzero((norm@dp)>1.e-10)
 # A swept solid is its initial volume plus the prisms swept out by forward-facing boundary triangles.
 bins={}
 for ix in use:
  a=tri[ix];key=tuple(np.floor(a.mean(0)/3.8).astype(int));pr=M(m.Mesh64(np.ascontiguousarray(np.vstack((a,a+dp))),face));bins.setdefault(key,[]).append(pr)
 pieces=[union(gs) for gs in bins.values()];print(len(use),len(pieces),flush=True);return union([g,*pieces])
if __name__=='__main__':
 gg=geom(here/'P86_alivio_interior.npz');body=geom(T/'microduck15print/P44.npz');a=time.time();sw=sweep_exact(gg,[0,0,8]);bad=sw^body;check=dict(volumen_barrido_mm3=sw.volume(),estado=str(sw.status()),volumen_interseccion_barrido_con_P44_mm3=bad.volume(),volumen_interseccion_asiento_mm3=(gg^body).volume(),cuerpos=[float(q.volume()) for q in bad.decompose()],tiempo_s=time.time()-a);saveg('P86_ultimo_tramo',sw);print(check,flush=True);(here/'P86_asiento_continuo_P44.json').write_text(json.dumps(check,indent=1),'utf8')
