from rebaje_tapa import *
import shutil,trimesh,hashlib,itertools
from scipy.spatial import cKDTree
g8=r/'V16_R1_G8_Ensayo_de_montaje';template=next((g8/'STL_POR_COLORES').rglob('86_*.stl'));m0=trimesh.load(template,force='mesh');vv,ff=verts(lid);tree0=cKDTree(m0.vertices);mid=lambda a:(a.max(0)+a.min(0))/2
results=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product((-1,1),repeat=3):
  mat=np.eye(3)[list(perm)]*np.asarray(signs)[:,None]
  if np.linalg.det(mat)<.99:continue
  tr=mid(m0.vertices)-mat@mid(vv);q=vv@mat.T+tr;sel=np.arange(0,len(q),max(1,len(q)//380))
  results.append((float(tree0.query(q[sel])[0].max()),mat,tr))
err,rot,offset=min(results,key=lambda itm:itm[0]);q=vv@rot.T+offset
err=max(tree0.query(q)[0].max(),cKDTree(q).query(m0.vertices)[0].max())
assert err<.005,(err,rot,offset);print('registro',err,rot.tolist(),offset,flush=True)
work=r/'V16_R1_G9_Ensayo_de_cierre';out=work/'STL_POR_COLORES'/template.parent.name;out.mkdir(exist_ok=True,parents=True);chk=work/'Verificacion';chk.mkdir(exist_ok=True)
lidnew=geom(here/'P86_alivio_interior.npz');v,f=verts(lidnew);new=trimesh.Trimesh(v@rot.T+offset,f,process=True);file=out/'86_Tapa_curva_con_alivio_interior.stl'
new.export(file);read=trimesh.load(file,force='mesh');parts=read.split(only_watertight=False);print('componentes',len(parts),read.is_watertight,flush=True)
if len(parts)!=1:
 parts=[c for c in parts if c.volume>1.e-6];assert len(parts)==1 and parts[0].is_watertight;parts[0].export(file);read=trimesh.load(file,force='mesh')
assert read.is_watertight and read.is_winding_consistent and abs(read.volume-lidnew.volume())<.03 and abs(read.bounds[0,2])<.003
proof=dict(error_registro_con_STL_G8_mm=err,rotacion=rot.tolist(),traslacion=offset.tolist(),volumen_mm3=read.volume,malla_cerrada=read.is_watertight,Z_inicial_mm=float(read.bounds[0,2]),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),membranas_nulas_retiradas=0,simplificacion_mm=0)
(chk/'Preparacion_STL.json').write_text(json.dumps({'P86':proof},indent=1),'utf8')
