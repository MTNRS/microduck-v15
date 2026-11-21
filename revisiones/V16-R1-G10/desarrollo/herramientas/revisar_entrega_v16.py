from pathlib import Path, PurePosixPath
import argparse,csv,hashlib,json,re,xml.etree.ElementTree as ET,zipfile
from collections import Counter
from urllib.parse import unquote,urlsplit
import numpy as np
from auditar_impresion import sha,load_facets,surface_stats
from concurrent.futures import ThreadPoolExecutor

def doc(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def hashstream(stream):
    digest=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def inventory(root,archive):
    sums=root/'SHA256SUMS.txt'; expected={}
    for line in sums.read_text(encoding='utf-8').splitlines():
        digest,name=line.split('  ',1)
        path=PurePosixPath(name)
        assert not path.is_absolute() and not any(x in ('.','..') or ':' in x or '\\' in x for x in path.parts),name
        assert name not in expected and re.fullmatch('[0-9a-f]{64}',digest)
        expected[name]=digest
    present={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert present==set(expected)|{'SHA256SUMS.txt'},present.symmetric_difference(set(expected)|{'SHA256SUMS.txt'})
    expected['SHA256SUMS.txt']=sha(sums)
    with zipfile.ZipFile(archive) as z:
        assert len(z.infolist())==len(expected)==len(set(x.casefold() for x in z.namelist()))
        assert set(z.namelist())==set(expected)
        for name,h in expected.items():
            assert sha(root/name)==h,name
            with z.open(name) as stream:assert hashstream(stream)==h,name
    print('ZIP equality',len(expected),'files',flush=True)
    return len(expected)

def links(root):
    broken=[];n=0;files=sorted(p for p in root.rglob('*.md') if 'third_party' not in p.relative_to(root).parts)
    for f in files:
        for u in re.findall(r'\]\(<?([^\s>)]+)>?',f.read_text(encoding='utf-8-sig')):
            url=urlsplit(u)
            if url.scheme or not url.path:continue
            n+=1
            dst=(f.parent/unquote(url.path)).resolve()
            if not dst.is_relative_to(root.resolve()) or not dst.exists():broken.append({'file':f.relative_to(root).as_posix(),'link':u})
    return {'links':n,'files':len(files),'broken':broken}

def xyz_order(triangles):
    # Cyclic reorder for equal meshes without reliance on the XML face order.
    k=np.lexsort((triangles[:,:,2],triangles[:,:,1],triangles[:,:,0]),axis=1)
    n=np.take_along_axis(triangles,k[:,:,None],axis=1)
    keys=n.reshape(-1,9)
    return keys[np.lexsort(keys.T[::-1])]

def same_mesh_xml(source,xml):
    namespace={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    model=ET.fromstring(xml)
    assert model.attrib.get('unit')=='millimeter'
    objs=model.findall('c:resources/c:object',namespace)
    assert len(objs)==1
    vertices=np.asarray([[float(x.get(k)) for k in ('x','y','z')] for x in objs[0].findall('c:mesh/c:vertices/c:vertex',namespace)],np.float64)
    faces=np.asarray([[int(t.get(k)) for k in ('v1','v2','v3')] for t in objs[0].findall('c:mesh/c:triangles/c:triangle',namespace)])
    b=vertices[faces]
    assert b.shape==source.shape,(b.shape,source.shape)
    shift=b.min(axis=(0,1))-source.min(axis=(0,1))
    build=model.findall('c:build/c:item',namespace)
    assert len(build)==1 and build[0].get('objectid')==objs[0].get('id')
    if build[0].get('transform'):
        t=np.array(build[0].get('transform').split(),float).reshape(4,3)
        assert np.allclose(t[:3],np.eye(3),atol=1e-7)
    b=b-shift
    drift=float(np.max(np.abs(source-b)))
    if drift>0.00006:
        drift=float(np.max(np.abs(xyz_order(source)-xyz_order(b))))
    return {'faces':len(faces),'origin_shift_mm':shift.tolist(),'max_coordinate_delta_mm':drift,'pass':drift<=.00006}

def run(args):
    root=args.root.resolve()
    n=inventory(root,args.archive)
    m=doc(root/'MANIFIESTO_STL_V16.json')
    rs={r['id']:r for r in doc(root/'VERIFICACION_LAMINADO_V16.json')['parts']}
    xs={r['id']:r for r in m['parts']}
    assert set(xs)==set(rs)=={f'P{i:02}' for i in range(1,81)}
    actual={p.relative_to(root).as_posix() for p in (root/'STL_POR_COLORES').rglob('*.stl')}
    assert set(r['file'] for r in xs.values())==actual
    checks={}
    for id,r in xs.items():
        x=rs[id]
        assert x['stl_sha256']==r['sha256']==sha(root/r['file']) and x['ok'] and x['slicer_exit']==0 and x['model_layers']>0
        assert x['config']==r['process'],id
        assert all(val==0 for row in x['repairs'] for val in row.values()),id
        if not args.skip_topology:
            s=surface_stats(load_facets(root/r['file']))
            assert s['facets']==r['facets'] and not any(s[k] for k in ('zero_area','duplicate_faces','edges_not_two','inconsistent_edges')),id
        if r['pauses']:
            f=next((root/'PROYECTOS_PRUSA_PAUSAS').glob(id+'_*'))
            assert x['project_sha256']==sha(f)
            with zipfile.ZipFile(f) as z:
                assert not any(name.endswith(('.gcode','.bgcode')) for name in z.namelist())
                xml=ET.fromstring(z.read('Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml'))
                events=xml.findall('code')
                assert all(t.get('type')=='1' and t.get('gcode')=='' for t in events)
                layers=[float(e.get('print_z')) for e in events]
                assert layers==x['pause_actual']==x['pause_expected'],id
                assert len(events)==len(r['pauses'])
                for event,plan in zip(events,r['pauses']):
                    assert all(nut in event.get('extra') for nut in plan['insert_names'])
                q=same_mesh_xml(load_facets(root/r['file']),z.read('3D/3dmodel.model'))
                checks[id]={'events':layers,**q}
                print('3MF',id,'match',q['pass'],'max delta',q['max_coordinate_delta_mm'],flush=True)
    assert len(checks)==len(list((root/'PROYECTOS_PRUSA_PAUSAS').glob('*.3mf')))==9
    assert sum(len(x['events']) for x in checks.values())==12
    with (root/'LISTA_IMPRESION_V16.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==80
    for r in rows:
        x=xs[r['id']]
        assert r['file']==x['file'] and r['material']==x['material']
        for k in ('layer_height_mm','first_layer_height_mm','perimeters','infill_percent','brim_mm','raft_layers','support_top_gap_mm'):
            assert float(r[k])==x['process'][k],(r['id'],k)
    corridors=doc(root/'VERIFICACION_CORREDORES_V16.json')
    assert corridors['clear']==corridors['checked']==len(corridors['proof'])==26
    assert all(c['V16_stl_sha256']==xs[c['id']]['sha256'] and c['clear'] for c in corridors['proof'])
    doccheck=links(root)
    result={'zip_sha256':sha(args.archive),'zip_files_verified':n,'stl_receipts_verified':80,
            'stl_topology_rechecked':not args.skip_topology,'prusa_projects':checks,'pause_events':12,'nut_corridors':26,
            'documentation':doccheck,'physical_validation':False}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('DOCUMENTATION',doccheck,flush=True)
    return int(bool(doccheck['broken']) or any(not r['pass'] for r in checks.values()))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('archive',type=Path);p.add_argument('report',type=Path);p.add_argument('--skip-topology',action='store_true');raise SystemExit(run(p.parse_args()))
