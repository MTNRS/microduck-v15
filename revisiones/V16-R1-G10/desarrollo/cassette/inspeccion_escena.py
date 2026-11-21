import bpy
for s in bpy.data.scenes:
 objs=[o for o in s.objects if 'P86' in o.name or ('tapa' in o.name.lower() and 'registro' in o.name.lower())]
 print(s.name,s.frame_end,[(o.name,o.type,tuple(round(v,4) for v in o.location),str(o.parent),o.get('ID'),len(o.data.vertices) if o.type=='MESH' else None) for o in objs])
 if s.name.startswith('04'):
  print('MARCAS',[(m.frame,m.name) for m in s.timeline_markers])
  for o in s.objects:
   if o.animation_data and (o in objs or o.type=='EMPTY' or 'tapa' in o.name.lower()):
    print('anim',o.name,tuple(o.location),o.animation_data.action,[(c.data_path,[(k.co.x,round(k.co.y,3)) for k in c.keyframe_points][:18]) for c in o.animation_data.action.fcurves][:5] if o.animation_data.action else None)
