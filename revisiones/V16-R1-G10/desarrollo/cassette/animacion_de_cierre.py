import bpy,numpy as np,json
from pathlib import Path
r=Path(bpy.data.filepath).parent.parent;folder=r/'V16_R1_G9_Ensayo_de_cierre';ver=folder/'Verificacion';work=r/'trabajo/cierre_G9';arr=np.load(work/'P86_alivio_interior.npz');v=arr['v'];f=arr['f'];old=np.load(Path(__import__('tempfile').gettempdir())/'md8work/P86.npz')['v'];sc=next(s for s in bpy.data.scenes if s.name.startswith('04'));win=bpy.context.window_manager.windows[0];seen=[];mesh=None;part=None
for s in bpy.data.scenes:
 for o in s.objects:
  if o.type!='MESH' or not o.name.startswith('P86 ·'):continue
  coords=np.empty(len(o.data.vertices)*3,'f');o.data.vertices.foreach_get('co',coords);p=coords.reshape(-1,3);assert len(p)==len(old) and np.allclose(p.min(0),old.min(0),atol=3.e-5) and np.allclose(p.max(0),old.max(0),atol=3.e-5)
  if mesh is None:
   mesh=bpy.data.meshes.new('P86 · alivio de los tres retornos de masa');mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update();assert not mesh.validate()
   for mat in o.data.materials:mesh.materials.append(mat)
  o.data=mesh;o['Revisión']='G9';seen.append(s.name)
  if s==sc:part=o
assert len(seen)==3 and part is not None
poses=[(1,(-90,0,14)),(39,(-90,0,14)),(75,(-18,0,14)),(95,(0,0,10)),(110,(0,0,10)),(145,(0,0,0))]
ac=part.animation_data.action
for fc in list(ac.fcurves):
 if fc.data_path=='location':ac.fcurves.remove(fc)
for fr,pt in poses:part.location=pt;part.keyframe_insert(data_path='location',frame=fr)
for fc in ac.fcurves:
 if fc.data_path=='location':
  for k in fc.keyframe_points:k.interpolation='LINEAR'
for m in sc.timeline_markers:
 if m.frame==95:m.name='03 · Bajar en vertical los últimos 10 mm'
sc.timeline_markers.new('Deslizar 18 mm y bajar de 14 a 10 mm',frame=75)
for o in sc.objects:
 if o.type!='FONT':continue
 txt=o.data.body
 if 'se desplaza 90 mm' in txt:o.data.body='Avanza 72 mm a 14 mm de altura. En los últimos 18 mm, desciende hasta 10 mm.'
 if 'Bajar la tapa 12 mm' in txt:o.data.body='03   Bajar la tapa 10 mm'
 if 'Comprobar las holguras' in txt:o.data.body='G9 · Tapa comprobada ante los 153 conductores. El arnés interior sigue en ensayo.'
sc['P86']='Entrada trasera a +14 mm. Desde −18 mm avanzar y bajar hasta +10 mm. Asentar verticalmente y poner los cuatro tornillos.'
win.scene=sc;record=[]
for fr in range(1,146):
 sc.frame_set(fr);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();loc=np.array(part.evaluated_get(dg).matrix_world.translation);goal=np.array([np.interp(fr,[p[0] for p in poses],[p[1][i] for p in poses]) for i in range(3)]);assert np.linalg.norm(loc-goal)<.0001,(fr,loc,goal)
 record.append(float(np.linalg.norm(loc-goal)))
vv=np.empty(len(mesh.vertices)*3,'f');mesh.vertices.foreach_get('co',vv);mb=vv.reshape(-1,3).astype('d');t=mb[f];volume=abs(float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6))
prep=json.loads((ver/'Preparacion_STL.json').read_text('utf8'));svol=prep['P86']['volumen_mm3'];assert abs(volume-svol)<.02
fp=ver/'Despiece_86_en_Blender.json';x=json.loads(fp.read_text('utf8'));k=next(k for k in x if 'comprobacion' in k);x[k]['P86'].update(volumen_del_STL_mm3=svol,volumen_blender_mm3=volume,error_absoluto_mm3=abs(svol-volume));fp.write_text(json.dumps(x,indent=1,ensure_ascii=False),'utf8')
rp=dict(escenas=seen,fotogramas_verificados=len(record),error_maximo_trayectoria_mm=max(record),volumen_Blender_mm3=volume,volumen_STL_mm3=svol,vertices_de_P86=len(v),poses=poses)
harness={w['id']:w for w in json.loads((folder/'Tendido_15_motores_en_ensayo.json').read_text('utf8'))['hilos']};sc1=next(s for s in bpy.data.scenes if s.name.startswith('01'))
oldcoll=next(c for c in sc.collection.children_recursive if 'Tendido · Cierre' in c.name)
for o in list(oldcoll.objects):
 if o.get('ID') in harness:oldcoll.objects.unlink(o)
seenw=set()
for o in sc1.objects:
 n=o.get('ID')
 if n not in harness or o.type!='CURVE':continue
 assert n not in seenw
 coords=np.empty(len(o.data.splines[0].points)*4,'f');o.data.splines[0].points.foreach_get('co',coords)
 assert np.max(abs(coords.reshape(-1,4)[:,:3]-np.array(harness[n]['closed'])))<.00005
 oldcoll.objects.link(o);seenw.add(n)
assert len(seenw)==153;rp['conductores_completos_en_la_escena_de_cierre']=len(seenw)
(ver/'Animacion_cierre_G9.json').write_text(json.dumps(rp,indent=1,ensure_ascii=False),'utf8')
for ar in win.screen.areas:
 if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.overlay.show_overlays=False
sc.frame_set(75);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Microduck_G9_arnes_y_montaje.blend'),compress=True);print('CHECK',rp,flush=True)
for fr,title in ((73,'P86_aproximacion'),(118,'P86_descenso'),(233,'P86_atornillado')):
 sc.frame_set(fr);sc.render.filepath=str(folder/(title+'.png'));bpy.ops.render.render(scene=sc.name,write_still=True)
