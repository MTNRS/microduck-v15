from __future__ import annotations
import argparse,csv,hashlib,json,math,re,struct
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
V15=ROOT.parent/'microduck-v15-publico'/'fabricacion'
D=Path(r"C:/Users/freak/Documents/ChatGPT/Jarvis/outputs/microduck-cuerpo-suave-v15/fabricacion-v15")/'KIT_V15_R2_FABRICACION'/'DIAGNOSTICO_NO_IMPRIMIR_GCODE'
VERTICES=re.compile(rb'^\s*vertex\s+([^\r\n]+)',re.MULTILINE)
WORD=re.compile(r'([XYE])([-+]?\d*(?:\.\d+)?(?:[eE][-+]?\d+)?)')
SUPPORT={'Support material','Support material interface'}
IGNORED={'Custom','Skirt/Brim','Wipe tower'}

def sha(path):
    with path.open('rb') as stream:
        h=hashlib.sha256()
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
        return h.hexdigest()

def load_facets(path):
    raw=path.read_bytes()
    if len(raw)>=84 and 84+50*struct.unpack_from('<I',raw,80)[0]==len(raw):
        record=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')])
        return np.frombuffer(raw,dtype=record,offset=84)['vertices'].copy()
    found=VERTICES.findall(raw)
    xyz=np.fromstring(b' '.join(found),dtype=np.float64,sep=' ')
    if not found or xyz.size != len(found)*3 or xyz.size%9 or not np.isfinite(xyz).all():
        raise ValueError(f'STL inválido: {path}')
    return xyz.reshape(-1,3,3).astype(np.float32)

def surface_stats(facets):
    xyz=facets.astype(np.float64)
    ab=xyz[:,1]-xyz[:,0];ac=xyz[:,2]-xyz[:,0];bc=xyz[:,2]-xyz[:,1]
    lens=np.column_stack([(x*x).sum(axis=1) for x in (ab,ac,bc)])
    area=np.linalg.norm(np.cross(ab,ac),axis=1)/2
    quality=np.divide(4*math.sqrt(3)*area,lens.sum(axis=1),out=np.zeros(len(area)),where=lens.sum(axis=1)>0)
    v,ids=np.unique(facets.reshape(-1,3),axis=0,return_inverse=True)
    f=ids.reshape(-1,3)
    directed=f[:,[[0,1],[1,2],[2,0]]].reshape(-1,2)
    _,i,n=np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True)
    edge_winding=np.bincount(i,weights=np.where(directed[:,0]<directed[:,1],1,-1))
    return {
        'facets':len(f),'vertices_f32':len(v),
        'zero_area':int(np.sum(area==0)),
        'duplicate_faces':int(len(f)-len(np.unique(np.sort(f,axis=1),axis=0))),
        'edges_not_two':int(np.sum(n!=2)),
        'inconsistent_edges':int(np.sum(edge_winding!=0)),
        'slivers_quality_below_0p001':int(np.sum(quality<.001)),
        'tiny_area_below_1e_6_mm2':int(np.sum(area<1e-6)),
        'shortest_edge_mm':float(np.sqrt(lens.min())),
        'minimum_z_mm':float(v[:,2].min()),
        'max_z_mm':float(v[:,2].max()),
        'signed_volume_mm3':float(np.einsum('ij,ij->i',xyz[:,0],np.cross(xyz[:,1],xyz[:,2])).sum()/6),
        'base_facet_area_mm2':float(area[np.max(abs(xyz[:,:,2]-v[:,2].min()),axis=1)<.001].sum())
    }

def paths(path):
    pos={'X':0.,'Y':0.,'E':0.}
    typ='Custom';z=None;absolute=True
    model=defaultdict(float);support=defaultdict(float)
    config={};sizes=Counter();retraction=0.
    with path.open(encoding='utf-8',errors='strict') as stream:
        for line in stream:
            if line.startswith(';TYPE:'):typ=line[6:].strip();continue
            if line.startswith(';Z:'):z=round(float(line[3:]),5);continue
            if line.startswith('; '):
                k,sep,val=line[2:].strip().partition(' = ')
                if sep and k in {'perimeter_generator','min_feature_size','min_bead_width','filament_type','first_layer_height','raft_layers','nozzle_diameter','temperature'}:
                    config[k]=val
                continue
            if line.startswith('M82'):absolute=True;continue
            if line.startswith('M83'):absolute=False;continue
            if not line.startswith(('G0 ','G1 ','G92 ')):continue
            words={k:float(v) for k,v in WORD.findall(line.split(';',1)[0]) if v}
            if line.startswith('G92 '):
                pos.update(words);continue
            x,y=words.get('X',pos['X']),words.get('Y',pos['Y'])
            e=words.get('E',pos['E'] if absolute else 0)
            de=e-pos['E'] if absolute else e
            distance=math.hypot(x-pos['X'],y-pos['Y'])
            if absolute:pos['E']=e
            pos['X'],pos['Y']=x,y
            if z is None or distance<=1e-6 or de<=1e-7 or typ in IGNORED:continue
            volume=de*math.pi*1.75**2/4
            (support if typ in SUPPORT else model)[z]+=volume
            sizes[typ]+=1
    vm,vs=sum(model.values()),sum(support.values())
    return {
        'model_layers':len(model),'support_layers':len(support),
        'model_extrusion_mm3':vm,'support_extrusion_mm3':vs,
        'support_to_model_ratio':vs/vm if vm else None,
        'first_model_z_mm':min(model,default=None),
        'first_model_extrusion_mm3':model[min(model)] if model else None,
        'first_support_z_mm':min(support,default=None),
        'feature_types':dict(sizes),'slicer_profile':config
    }

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--mesh-only',action='store_true')
    args.add_argument('--ids',nargs='+')
    opt=args.parse_args()
    manifest=json.loads((V15/'STL_MANIFIESTO_V15.json').read_text(encoding='utf-8'))
    target=ROOT/'trabajo'/'auditoria-v15';target.mkdir(exist_ok=True,parents=True)
    result=[]
    for r in manifest['parts']:
        if opt.ids and r['id'] not in opt.ids:continue
        p=V15/r['file'].replace('\\','/')
        if sha(p)!=r['sha256']:raise RuntimeError(f'{p.name}: distinto del kit de partida')
        s=surface_stats(load_facets(p))
        record={'id':r['id'],'name':r['name'],'file':p.name,'sha256':r['sha256'],
                'material':r['material'],'raft_layers':r['raft_layers'],
                'cad_bed_contact_mm2':r['orientation']['bed_contact_area_mm2'],**s}
        if not opt.mesh_only:record.update(paths(D/(r['id']+'.gcode')))
        result.append(record)
        print(r['id'],s['facets'],'topology',s['zero_area']+s['duplicate_faces']+s['edges_not_two']+s['inconsistent_edges'],
              'base',round(s['base_facet_area_mm2'],2),'support/model',round(record.get('support_to_model_ratio') or 0,2),flush=True)
    j=target/('V15_GEOMETRIA.json' if opt.mesh_only else 'V15_GEOMETRIA_Y_TRAYECTORIAS.json')
    j.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(j,flush=True)

if __name__=='__main__':main()
