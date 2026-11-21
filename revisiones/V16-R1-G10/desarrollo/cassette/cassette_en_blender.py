import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
r=Path(bpy.data.filepath).parent.parent;old=Path(bpy.data.filepath).parent;g=r/'V16_R1_G10_Ensayo_de_cassette';work=r/'trabajo/cierre_G9';v=g/'Verificacion';win=bpy.context.window_manager.windows[0]
def read(f):return json.loads(f.read_text('utf8'))
def wr(f,j):f.write_text(json.dumps(j,indent=1,ensure_ascii=False),'utf8')
def byid(folder):return {w['id']:w for w in read(folder/'Tendido_15_motores_en_ensayo.json')['hilos']}
ws=byid(g);baseline=byid(old);changed={k for k in ws if ws[k]['closed']!=baseline[k]['closed']}
def coords(o):
 p=o.data.splines[0].points;q=np.empty(len(p)*4,'f');p.foreach_get('co',q);return q.reshape(-1,4)[:,:3]
def spline(o,p):
 assert not o.data.shape_keys
 o.data.splines.clear();sp=o.data.splines.new('POLY');sp.points.add(len(p)-1);sp.points.foreach_set('co',np.column_stack((p,np.ones(len(p)))).astype('f').ravel())
nw=np.load(work/'P45_BM_canal_sin_isla.npz');x=nw['v'];f=nw['f'];full=bpy.data.meshes.new('P45 · canal de montaje BM');full.from_pydata(x.tolist(),[],f.tolist());full.update();assert not full.validate()
def sect():
 data=full.copy();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00005,plane_co=(0,0,137.5),plane_no=(0,0,1),clear_outer=True);bm.to_mesh(data);bm.free();return data
section=sect();sizes=[];objs=set();formed=np.array(read(work/'BM_desvio_junto_al_pad.json')['tramo'])
for s in bpy.data.scenes:
 for o in s.objects:
  if o.name in objs:continue
  objs.add(o.name);n=o.get('ID')
  if o.name.startswith('P45 ·') and o.type=='MESH':
   for mat in o.data.materials:
    if mat and full.materials.find(mat.name)<0:full.materials.append(mat)
   o.data=section if 'sección' in o.name else full;sizes.append((s.name,o.name));o['Revisión']='G10'
  if n in changed and o.type=='CURVE':
   existing=coords(o);oldq=np.asarray(baseline[n]['closed'])
   if existing.shape==oldq.shape and np.allclose(existing,oldq,atol=.00005):spline(o,np.array(ws[n]['closed']))
   elif n=='W003' and s.name.startswith('09'):
    q=np.array(ws[n]['closed']);assert np.allclose(q[:len(existing)],existing,atol=.00005)
  if o.name.startswith(('BM · salida soldada','BM · salida local')) and o.type=='CURVE':spline(o,formed)
sc=next(s for s in bpy.data.scenes if s.name.startswith('06'))
photo=read(work/'PCM_hilos_frente_a_fotografia.json')['hilos']
for row in photo.values():
 pad=sc.objects.get('Pad '+row['pad'])
 if not pad:continue
 xy=row['centro_foto_xy_mm'];pad.location.x,pad.location.y=xy
 if row['pad'] in ('B+','B−','BM'):
  # The three square lands are distinguishable in the photograph. Their outlines are nominal.
  bm=bmesh.new();bmesh.ops.create_cube(bm,size=1.)
  for vert in bm.verts:vert.co.x*=4.1;vert.co.y*=4.3;vert.co.z*=.14
  m=bpy.data.meshes.new('Zona de soldadura '+row['pad']);bm.to_mesh(m);bm.free();pad.data=m
 pad['Contorno']='Aproximado a partir de la fotografía Mantech, sin cotas de fabricación.'
for o in sc.objects:
 if o.type=='FONT' and 'último tramo salva' in o.data.body:o.data.body='El cable BM entra con la placa. Su curva pasa por el canal interior de P45.'
sc['P45 G10']='Canal para el hilo BM. Entrada diagonal de la placa. Vista en sección hasta z = 137,5 mm.'
for num in ('01','04','05'):
 s=next(s for s in bpy.data.scenes if s.name.startswith(num));full_wires={o.get('ID'):o for o in s.objects if o.type=='CURVE' and o.get('ID') in ws};assert len(full_wires)==153
 for n,o in full_wires.items():
  q=coords(o);p=np.array(ws[n]['closed']);assert q.shape==p.shape and np.max(abs(p-q))<.00005,(s.name,n)
# A second camera shows the narrow entry without hiding it behind the assembled shell.
macro=bpy.data.scenes.new('10 · Canal BM del cassette');macro.render.engine='BLENDER_WORKBENCH';macro.display.shading.color_type='OBJECT';macro.display.shading.light='STUDIO';macro.display.shading.show_shadows=True;macro.display.shading.show_cavity=True;macro.display.shading.cavity_type='WORLD';macro.display.shading.show_specular_highlight=False;macro.display.shading.background_type='WORLD';macro.world=bpy.data.worlds.new('Fondo de inspección');macro.world.color=(.09,.11,.14)
win.scene=sc;sc.frame_set(120);bpy.context.view_layer.update()
for o in sc.objects:
 if o.name.startswith(('Mantech 250040','Pad ','BM · salida soldada','P45 · sección')) or o.name.startswith(('P+ · salida soldada','P− · salida soldada')):
  cp=o.copy();cp.animation_data_clear();cp.hide_viewport=False;cp.hide_render=False;macro.collection.objects.link(cp)
  if o.name.startswith('P45'):
   cp.location=(0,0,0);data=full.copy();bm=bmesh.new();bm.from_mesh(data)
   cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00003,plane_co=(0,0,132.89),plane_no=(0,0,1),clear_outer=True)
   border=[e for e in cut['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
   if border:bmesh.ops.triangle_fill(bm,edges=border,use_beauty=True)
   bm.to_mesh(data);bm.free();cp.data=data
cam=bpy.data.objects.new('Detalle del canal y pad BM',bpy.data.cameras.new('Detalle ortográfico'));macro.collection.objects.link(cam);macro.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=28;cam.data.clip_start=.02;cam.data.clip_end=300
target=Vector((-65,-19.8,132.8));cam.location=target+Vector((-4.5,-15,47));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();macro.render.resolution_x=1050;macro.render.resolution_y=680;macro.render.resolution_percentage=100
macro['Cable amarillo']='W003, desde BM al adaptador de equilibrado del pack.';macro['Cassette']='P45, seccionado solo en esta vista para enseñar el canal interior.'
win.scene=macro
for ar in win.screen.areas:
 if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.overlay.show_overlays=False;ar.spaces.active.shading.color_type='OBJECT'
vol=abs(np.einsum('ij,ij->i',x[f[:,0]],np.cross(x[f[:,1]],x[f[:,2]])).sum()/6);stl=read(v/'Preparacion_STL.json')['P45']['volumen_mm3'];assert abs(vol-stl)<.02
proof=read(v/'Despiece_86_en_Blender.json');k=next(k for k in proof if 'comprobacion' in k);proof[k]['P45'].update(volumen_del_STL_mm3=stl,volumen_blender_mm3=float(vol),error_absoluto_mm3=abs(float(vol)-stl));wr(v/'Despiece_86_en_Blender.json',proof)
wr(v/'Cassette_G10_en_Blender.json',dict(escenas_con_P45=sizes,escenas_con_153_hilos_comprobados=['01','04','05'],cables_actualizados=sorted(changed),volumen_STL=stl,volumen_Blender=float(vol)))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(g/'Microduck_G10_arnes_y_montaje.blend'),compress=True)
macro.render.filepath=str(g/'Canal_BM_de_P45.png');bpy.ops.render.render(scene=macro.name,write_still=True)
