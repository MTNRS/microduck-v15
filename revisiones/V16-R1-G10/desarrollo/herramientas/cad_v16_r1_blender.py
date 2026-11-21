import bpy,hashlib,json,sys
from pathlib import Path
import numpy as np
P=Path(r"C:/Users/freak/Documents/ChatGPT/Robots/microduck-v16")
target=P/'Microduck_V16_R1.blend'
proof=P/'trabajo/BLENDER_V16_R1.json'
name='12CASE_TORSO_CONTINUO'
def fingerprint(o):
    v=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',v)
    f=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',f)
    return hashlib.sha256(v.tobytes()+f.tobytes()+np.array(o.matrix_world,dtype=float).tobytes()).hexdigest()
def prints():
    return {o.name:fingerprint(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('fabrication_role')=='PRINT'}
bpy.context.view_layer.update()
if '--verify' in sys.argv:
    j=json.loads(proof.read_text(encoding='utf-8'))
    assert prints()==j['fingerprints']
    with target.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==j['blend_sha256']
    j['reopened_verified']=True;proof.write_text(json.dumps(j,indent=2),encoding='utf-8')
    print('R1 CAD reread verified',len(j['fingerprints']))
    raise SystemExit(0)
assert not target.exists()
before=prints();assert len(before)==80
with np.load(P/'trabajo/p44_final_blender.npz') as z:
    world=z['vertices'];faces=z['faces']
o=bpy.data.objects[name];old=o.data;M=np.array(o.matrix_world,dtype=float);im=np.linalg.inv(M)
new=bpy.data.meshes.new(name+'_V16_R1')
local=world@im[:3,:3].T+im[:3,3]
new.from_pydata(local.tolist(),[],faces.tolist());new.update()
for m in old.materials:
    if m:new.materials.append(m)
for face in new.polygons:face.use_smooth=True
new.set_sharp_from_angle(angle=np.deg2rad(35))
o.data=new;o['v16_change']='Borde CAP06 revisado. La pieza se exporta con las pausas físicas de 45 y 46 mm.'
if old.users==0:bpy.data.meshes.remove(old)
bpy.context.view_layer.update()
checked=np.empty(len(new.vertices)*3,np.float32);new.vertices.foreach_get('co',checked)
err=float(np.max(abs(checked.reshape(-1,3)@M[:3,:3].T+M[:3,3]-world)));assert err<.0002
after=prints()
assert {n for n in before if after[n]!=before[n]}=={name}
scene=bpy.context.scene;scene.name='MICRODUCK_V16_R1'
scene['revision']='V16_R1'
t=bpy.data.texts.get('V16_LEER_PRIMERO')
if t:t.write('\nP44 corregido en el borde de servicio CAP06. Consulta GUIA_V16.md para las capas y pausas de impresión.')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=False,relative_remap=False,compress=False)
with target.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
proof.write_text(json.dumps({'blend_sha256':digest,'printed_parts':80,'updated_meshes':['P44','P45'],
                             'maximum_P44_match_to_STL_mm':err,'fingerprints':after,'reopened_verified':False},indent=2),encoding='utf-8')
print('R1 CAD saved',digest)
