from pathlib import Path
import json,math
import numpy as np
import manifold3d as mf
import trimesh
B=Path(r"C:/Users/freak/Documents/ChatGPT/Jarvis/outputs/microduck-cuerpo-suave-v15/fabricacion-v15")
P=Path(r"C:/Users/freak/Documents/ChatGPT/Robots/microduck-v16")/'trabajo'/'mandibula';P.mkdir(exist_ok=True,parents=True)
A=json.loads((B/'KIT_V15_R2_FABRICACION/ASSEMBLY_FABRICACION_CANDIDATO_V15.json').read_text(encoding='utf-8'))
rig=json.loads((B/'RIG_Y_MATERIALES_V15.json').read_text(encoding='utf-8'))
M=np.asarray(rig['bodies']['jaw_soft'],float)
# Original source-jaw-and-mount-anchors.json defines a jaw hinge in
# the head-roll body; the current jaw_soft body is that head-roll body.
pivot=M[:3,:3]@np.array([3.,0.,-18.])+M[:3,3]
axis=M[:3,:3]@np.array([0.,1.,0.]);axis/=np.linalg.norm(axis)
def load(row):
    with np.load(row['file']) as z:v=np.ascontiguousarray(z['vertices'],dtype=float);f=np.ascontiguousarray(z['faces'],dtype=np.uint64)
    so=mf.Manifold(mf.Mesh64(v,f))
    if so.status()!=mf.Error.NoError or so.is_empty():
        return None,v
    return so,v
names={'V7_HEAD_JAW_FIJO','V7_HEAD_LIP_LOWER_RELIEVED'}
move={};fixed={};fixed_mount=[];skipped=[]
lip_vertices=None
for role in ('parts','references'):
    for r in A[role]:
        n=r['name']
        if r['body']!='jaw_soft':continue
        if n.startswith('V7_HEAD_HW_JAW_'):
            fixed_mount.append(n);continue
        so,v=load(r)
        if so is None:
            skipped.append(n);continue
        if n in names:
            move[n]=so
            if n.endswith('LIP_LOWER_RELIEVED'):lip_vertices=v
        else:fixed[n]=so
assert len(move)==2 and lip_vertices is not None
tip=lip_vertices[lip_vertices[:,0]>lip_vertices[:,0].max()-.5].mean(axis=0)
def overlap(x,y):
    a=np.array(x.bounding_box()).reshape(2,3)
    b=np.array(y.bounding_box()).reshape(2,3)
    if np.any(np.minimum(a[1],b[1])<=np.maximum(a[0],b[0])):return 0.
    so=x^y
    if so.status()!=mf.Error.NoError:return None
    return float(so.volume())
out=[]
for deg in [0,2,5,10,15,20,25,30]:
    T=trimesh.transformations.rotation_matrix(math.radians(deg),axis,point=pivot)
    collisions=[];unknown=[]
    for n,solid in move.items():
        x=solid.transform(T[:3])
        for m,other in fixed.items():
            v=overlap(x,other)
            if v is None:unknown.append([n,m])
            elif v>.01:collisions.append({'moving':n,'fixed':m,'mm3':v})
    q=T[:3,:3]@tip+T[:3,3]
    row={'degrees':deg,'downward_tip_motion_mm':float(tip[2]-q[2]),'collisions_over_point01_mm3':sorted(collisions,key=lambda r:-r['mm3']),'unknown':unknown}
    out.append(row)
    print(deg,'tip',round(row['downward_tip_motion_mm'],2),'contacts',len(collisions),'max',round(max((r['mm3'] for r in collisions),default=0),2),flush=True)
j={'scope':'Hypothetical isolated jaw sweep around the upstream hinge after removing the fixed mounts. This does not enable a physical jaw or certify its path, force, reach or grasp.',
   'origin_mm':pivot.tolist(),'axis':axis.tolist(),'moving':sorted(move),'fixed_parts_checked':len(fixed),'fixed_mounts_excluded':fixed_mount,'skipped':skipped,'angles':out}
(P/'BARRIDO_HIPOTETICO_MANDIBULA_V16.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
