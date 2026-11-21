from canal_bm_p45 import *
from manifold3d import OpType
info=json.loads((here/'BM_desvio_junto_al_pad.json').read_text('utf8'));q=np.asarray(info['tramo']);stroke=np.array([[0,0,0],[0,4,-1],[0,28,-62]])
sw=geom(here/'BM_barrido_de_entrada.npz');rr=1.04;tool=mk(simplify(q),rr,stroke)
whole=raw-tool;pieces=sorted(whole.decompose(),key=lambda k:-k.volume());new=pieces[0];lost=union([raw^tool]+pieces[1:]);saveg('P45_BM_canal_sin_isla',new);saveg('P45_BM_recorte_definitivo',lost)
p65=geom(T/'microduck15print/P65.npz');p83=geom(T/'microduck15print/P83.npz');tray=mk(q,.55,np.array([[0,0,0],[0,0,22.]]));p83path=mk(q,.55,np.array([[0,0,0],[0,-68,0]]))
a,b,err=align();v,f=verts(new);st=trimesh.Trimesh(v@a.T+b,f,process=True)
wk=r/'V16_R1_G10_Ensayo_P45';out=wk/'STL_POR_COLORES'/reference.parent.name;out.mkdir(parents=True,exist_ok=True);ver=wk/'Verificacion';ver.mkdir(exist_ok=True)
path=out/'45_Cassette_con_canal_BM.stl';st.export(path);mesh=trimesh.load(path,force='mesh');parts=[o for o in mesh.split(only_watertight=False) if abs(o.volume)>.00001];assert len(parts)==1 and parts[0].is_watertight;parts[0].export(path);mesh=trimesh.load(path,force='mesh');assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split(only_watertight=False))==1
prep=dict(error_registro_con_STL_G9_mm=err,rotacion=a.tolist(),traslacion=b.tolist(),volumen_mm3=mesh.volume,malla_cerrada=True,Z_inicial_mm=float(mesh.bounds[0,2]),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(ver/'Preparacion_STL.json').write_text(json.dumps({'P45':prep},indent=1),'utf8')
out=dict(volumen_original_mm3=raw.volume(),retirado_mm3=lost.volume(),volumen_STL_mm3=mesh.volume,radio_herramienta_mm=rr,volumen_isla_suprimida_mm3=sum(g.volume() for g in pieces[1:]),margen_BM_entrada_P45_mm=sw.min_gap(new,3),choque_BM_con_antigua_P45_mm3=(sw^raw).volume(),choque_BM_entrada_corregida_mm3=(sw^new).volume(),margen_BM_entrada_P65_mm=tray.min_gap(p65,4),choque_BM_entrada_P65_mm3=(p65^tray).volume(),margen_BM_entrada_P83_mm=p83path.min_gap(p83,4),choque_BM_entrada_P83_mm3=(p83^p83path).volume(),error_volumen_cad_STL_mm3=abs(mesh.volume-new.volume()),piezas_impresas=1)
print(out,flush=True);(ver/'Geometria_del_canal_BM.json').write_text(json.dumps(out,indent=1),'utf8')
