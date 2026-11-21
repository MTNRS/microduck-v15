from pathlib import Path
from collections import defaultdict
import ast,json,re
import numpy as np
from auditar_impresion import V15,sha
from preparar_v16 import OUT,DIAG,read,write
old=Path(r"C:/Users/freak/Documents/ChatGPT/Jarvis/outputs/microduck-cuerpo-suave-v15/fabricacion-v15/52_comprobar_soportes_y_pausas.py")
src=ast.parse(old.read_text(encoding='utf-8-sig'))
fn=next(x for x in src.body if isinstance(x,ast.FunctionDef) and x.name=='gcode')
ns={'np':np,'re':re}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(old),'exec'),ns)
gcode=ns['gcode']
manifest={x['id']:x for x in read(OUT/'MANIFIESTO_STL_V16.json')['parts']}
prior={x['id']:x for x in read(V15/'STL_MANIFIESTO_V15.json')['parts']}
by=defaultdict(list)
for t in read(V15/'SOPORTES_Y_PAUSAS_V15.json')['tests']:by[t['id']].append(t)
actual={x['id']:x for x in read(OUT/'VERIFICACION_LAMINADO_V16.json')['parts']}
checks=[]
for id,tests in by.items():
    m=manifest[id];record=actual[id]
    assert record['ok'] and m['sha256']==record['stl_sha256']==sha(OUT/m['file'])
    assert m['process']['layer_height_mm']==.2 and m['process']['first_layer_height_mm']==.2 and m['process']['raft_layers']==0
    assert m['process']['supports_only_from_buildplate'] and m['process']['dont_support_bridges']
    assert m['world_to_v16_stl_matrix']==prior[id]['world_to_print_matrix']
    p=DIAG/id/'diagnostico.gcode'
    support,model=gcode(p)
    h=sha(p);dims=np.array(prior[id]['dimensions_mm'])
    center=np.r_[100-dims[0]/2,100-dims[1]/2,0]
    lo=model[:,0].min(0);hi=model[:,1].max(0)
    assert np.all(lo>=center-.6) and np.all(hi<=center+dims+.6)
    for t in tests:
        done=support[support[:,1,2]<=t['pause_Z_mm']+.0001]
        box=np.asarray(t['corridor_bbox_gcode_mm'],float)
        hits=int(np.sum(np.all(np.minimum(done[:,1],box[1])>np.maximum(done[:,0],box[0]),axis=1)))
        checks.append({'id':id,'tuerca':t['nut'],'pause_Z_mm':t['pause_Z_mm'],'support_boxes_intersecting':hits,
                       'V16_stl_sha256':m['sha256'],'diagnostic_gcode_sha256':h,'clear':hits==0})
    print(id,sum(c['clear'] for c in checks if c['id']==id),'/',len(tests),flush=True)
j={'checked':len(checks),'clear':sum(c['clear'] for c in checks),'scope':'Cajas conservadoras de soporte del laminado de diagnóstico. Prueba física pendiente.',
   'proof':checks}
write(OUT/'VERIFICACION_CORREDORES_V16.json',j)
assert j['clear']==j['checked']==26
