from canal_bm_p45 import *
from manifold3d import OpType
info=json.loads((here/'BM_desvio_junto_al_pad.json').read_text('utf8'));q=np.asarray(info['tramo']);stroke=np.array([[0,0,0],[0,4,-1],[0,28,-62]])
nodes=simplify(q);sw=geom(here/'BM_barrido_de_entrada.npz');out=[]
for radius in (.92,.97,1.02,1.07,1.12):
 tool=mk(nodes,radius,stroke)
 cut=max((raw^tool).decompose(),key=lambda k:k.volume())
 # A trailing loose sliver should stay off the print bed.
 new=max((raw-cut).decompose(),key=lambda k:k.volume())
 lost=raw-new
 row=dict(radio=radius,recorte_mm3=lost.volume(),holgura_barrido_mm=sw.min_gap(new,3),interseccion_mm3=(new^sw).volume(),componentes=len(new.decompose()))
 print(row,flush=True);out.append(row)
 if radius==1.02:
  saveg('P45_BM_canal_sin_isla',new);saveg('P45_BM_recorte_definitivo',lost)
(here/'P45_BM_variantes_de_holgura.json').write_text(json.dumps(out,indent=1),'utf8')
