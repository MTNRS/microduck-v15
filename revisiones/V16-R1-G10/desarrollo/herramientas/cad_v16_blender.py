import bpy,hashlib,json,sys
from pathlib import Path
import numpy as np
P=Path(r"C:/Users/freak/Documents/ChatGPT/Robots/microduck-v16")
out=P/'Microduck_V16_IMPRESION.blend'
proof=P/'trabajo/BLENDER_V16.json'
part='12CASE_TAPA_TRASERA_ENRASADA'
def data(o):
    coords=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',coords)
    faces=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',faces)
    return coords.reshape(-1,3),faces.reshape(-1,3)
def fingerprint(o):
    coords,faces=data(o)
    h=hashlib.sha256(coords.tobytes()+faces.tobytes())
    h.update(np.array(o.matrix_world,dtype=float).tobytes())
    return h.hexdigest()
def printed():
    return {o.name:fingerprint(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('fabrication_role')=='PRINT'}
bpy.context.view_layer.update()
if '--verify' in sys.argv:
    j=json.loads(proof.read_text(encoding='utf-8'))
    assert printed()==j['saved_print_fingerprints']
    with out.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==j['blend_sha256']
    j['reopened_verified']=True
    proof.write_text(json.dumps(j,indent=2),encoding='utf-8')
    print('V16 CAD re-opened: 80 printed objects match')
    raise SystemExit(0)
assert not out.exists()
before=printed();assert len(before)==80
o=bpy.data.objects[part];old=o.data
v,f=data(o);M=np.array(o.matrix_world,dtype=float)
with np.load(P/'trabajo/p45_v16_cad_source.npz') as z:
    assert np.array_equal(f,z['faces']) and np.max(np.abs(v@M[:3,:3].T+M[:3,3]-z['vertices']))<.0002
    keep=z['keep']
assert int((~keep).sum())==18
used=np.unique(f[keep]);lookup=np.full(len(v),-1,dtype=np.int64);lookup[used]=np.arange(len(used))
new=bpy.data.meshes.new(part+'_V16')
new.from_pydata(v[used].tolist(),[],lookup[f[keep]].tolist());new.update()
for mat in old.materials:
    if mat:new.materials.append(mat)
for face,original in zip(new.polygons,(face for face,retain in zip(old.polygons,keep) if retain)):
    face.use_smooth=original.use_smooth;face.material_index=original.material_index
if hasattr(new,'set_sharp_from_angle'):new.set_sharp_from_angle(angle=np.deg2rad(35.))
o.data=new
if old.users==0:bpy.data.meshes.remove(old)
scene=bpy.context.scene;scene.name='MICRODUCK_V16_IMPRESION'
scene['revision']='V16'
o['v16_change']='Dos cavidades selladas de aproximadamente 0,006 mm³ eliminadas. Superficie exterior conservada.'
t=bpy.data.texts.new('V16_LEER_PRIMERO')
t.write('Microduck V16, revisión de impresión. Orientaciones y capas se indican en LISTA_IMPRESION_V16.csv. P45 conserva su superficie exterior y elimina dos microcavidades internas. Verificar la primera unidad y el perfil de impresora.');t.use_module=False
bpy.context.view_layer.update()
after=printed();assert {k for k in after if before[k]!=after[k]}=={part}
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),check_existing=False,relative_remap=False,compress=False)
with out.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
proof.write_text(json.dumps({'blend_sha256':sha,'parts':80,'only_mesh_changed':part,'exterior_vertices_and_faces_preserved':True,'closed_cavity_faces_removed':18,'saved_print_fingerprints':after,'reopened_verified':False},indent=2),encoding='utf-8')
print('V16 CAD saved',sha)
