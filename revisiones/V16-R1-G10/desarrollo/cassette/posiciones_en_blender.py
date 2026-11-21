import bpy,numpy as np
from pathlib import Path
for sc in bpy.data.scenes:
 if not sc.name.startswith(('01','04','07')):continue
 w=bpy.context.window_manager.windows[0];w.scene=sc;sc.frame_set(1)
 for o in sc.objects:
  if o.type=='MESH' and o.name.startswith('P86'):
   vs=np.empty(len(o.data.vertices)*3,'f');o.data.vertices.foreach_get('co',vs);q=vs.reshape(-1,3)
   print('P86KEY',sc.name,o.data.name,q.min(0),q.max(0),np.array(o.matrix_world).tolist())
  if sc.name.startswith('04') and o.type=='FONT':
   print('TXT',o.data.body)
