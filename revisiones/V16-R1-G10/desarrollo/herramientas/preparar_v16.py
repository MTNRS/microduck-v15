from pathlib import Path
import argparse,concurrent.futures,csv,hashlib,json,math,shutil,subprocess
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from auditar_impresion import ROOT,V15,load_facets,sha,surface_stats,paths
from ensayar_orientaciones import SLICER,binary_stl,transform

WORK=ROOT/'trabajo'
OUT=ROOT/'V16_KIT_IMPRESION'
DIAG=WORK/'laminado-v16'
GEOMETRY_KEYS=('zero_area','duplicate_faces','edges_not_two','inconsistent_edges')
PAUSE_XML='Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml'
MODEL_XML='Metadata/Slic3r_PE_model.config'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path,doc):
    path.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def remove_lid_voids(facets):
    xyz,ind=np.unique(facets.reshape(-1,3),axis=0,return_inverse=True)
    mesh=trimesh.Trimesh(xyz,ind.reshape(-1,3),process=False)
    adj=mesh.face_adjacency
    graph=csr_matrix((np.ones(len(adj)),(adj[:,0],adj[:,1])),shape=(len(mesh.faces),len(mesh.faces)))
    _,labels=connected_components(graph,directed=False)
    keep=np.ones(len(facets),bool);removed=[]
    for label in np.unique(labels):
        mask=labels==label
        tri=facets[mask].astype(float)
        volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
        if -0.01<volume<0:
            keep[mask]=False;removed.append({'triangles':len(tri),'signed_volume_mm3':volume})
    if len(removed)!=2 or sum(x['triangles'] for x in removed)!=18:
        raise ValueError('Cavidades inesperadas en P45')
    return facets[keep],removed

def assemble():
    manifest=read(V15/'STL_MANIFIESTO_V15.json')
    plan=read(WORK/'PLAN_V16.json')
    OUT.mkdir(exist_ok=True,parents=True);DIAG.mkdir(exist_ok=True,parents=True)
    rows=[]
    for r in manifest['parts']:
        rel=Path(r['file'].replace('\\','/'));f=V15/rel;target=OUT/rel
        assert sha(f)==r['sha256'],r['id']
        a=load_facets(f);b=a;T=np.eye(4);voids=[]
        change=plan['parts'].get(r['id'],{})
        if change.get('remove_closed_voids'):
            b,voids=remove_lid_voids(b)
        patch=change.get('patch_stl')
        if patch:
            b=load_facets(WORK/patch)
        if 'matrix' in change:
            T=np.array(change['matrix'],dtype=float)
            assert np.allclose(T[:3,:3].T@T[:3,:3],np.eye(3)) and np.linalg.det(T[:3,:3])>0
        paused=bool(r['orientation'].get('required_pauses'))
        if paused:assert not change,'No reorientar ni cambiar capas/ajustes de pausas sin prueba separada'
        transformed=transform(b,T)
        error=float(np.max(np.abs((transformed.astype(float)-T[:3,3])@T[:3,:3]-b)))
        assert error<=0.00002,(r['id'],error)
        s=surface_stats(transformed)
        assert not any(s[k] for k in GEOMETRY_KEYS),r['id']
        target.parent.mkdir(exist_ok=True,parents=True);binary_stl(target,transformed)
        assert np.array_equal(transformed,load_facets(target)),r['id']
        process={
            'nozzle_mm':.4,'layer_height_mm':change.get('layer_mm',.2),
            'first_layer_height_mm':change.get('layer_mm',.2),'perimeters':r['perimeters'],
            'infill_percent':r['infill_percent'],'brim_mm':5,
            'support_top_gap_mm':.25,'support_threshold_deg':45,'support_enabled':True,
            'supports_only_from_buildplate':paused,'dont_support_bridges':paused,
            'raft_layers':change.get('raft_layers',r['raft_layers']),
            'perimeter_generator':'arachne'
        }
        combined=T@np.array(r['world_to_print_matrix'])
        row={'id':r['id'],'name':r['name'],'file':rel.as_posix(),'quantity':1,'color':r['color'],'material':r['material'],
             'sha256':sha(target),'source_v15_stl_sha256':r['sha256'],'source_v15_world_sha256':r['world_source_sha256'],
             'rotation_and_translation_from_v15_stl':T.tolist(),'world_to_v16_stl_matrix':combined.tolist(),
             'slicer_raise_z_to_bed_mm':-s['minimum_z_mm'],'max_inverse_rotation_deviation_mm':error,
             'mesh_changed':bool(voids or patch),'sealed_microvoids_removed':voids,
             'pauses':r['orientation'].get('required_pauses',[]),
             'process':process,'motivo':change.get('reason','Misma superficie en STL binario'),**s}
        rows.append(row)
    write(OUT/'MANIFIESTO_STL_V16.json',{'schema':'Microduck V16 / mm','physical_print_verified':False,'parts':rows})
    fields=['id','name','file','color','material','quantity','layer_height_mm','first_layer_height_mm','perimeters',
            'infill_percent','brim_mm','raft_layers','support_top_gap_mm','supports_only_from_buildplate','pauses','motivo']
    with (OUT/'LISTA_IMPRESION_V16.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({**r,**r['process'],'pauses':len(r['pauses'])})
    print('EXPORT',len(rows),'STL',sum(r['mesh_changed'] for r in rows),'mallas modificadas',flush=True)
    return rows

def check_slicer(r,*,always=False):
    options=r['process'];base=OUT/r['file'];p=DIAG/r['id'];p.mkdir(exist_ok=True,parents=True)
    result=p/'resultado.json';out=p/'diagnostico.gcode';tmp=p/'lectura.3mf'
    key=hashlib.sha256(json.dumps([r['sha256'],options,sha(Path(__file__))],sort_keys=True).encode()).hexdigest()
    if not always and result.exists():
        cached=read(result)
        if cached.get('key')==key and cached.get('ok'):return cached
    bed=['--center','100,100']
    cmd=[str(SLICER),'--export-3mf','--threads','2',*bed,'--output',str(tmp),str(base)]
    pr=subprocess.run(cmd,capture_output=True,text=True,timeout=200)
    if pr.returncode!=0:
        fail={'id':r['id'],'ok':False,'stage':'3mf','exit':pr.returncode,'error':pr.stderr[-2500:]}
        write(result,fail);return fail
    with ZipFile(tmp) as z:
        contents={name:z.read(name) for name in z.namelist()}
    model=ET.fromstring(contents[MODEL_XML])
    repairs=[{k:int(v) for k,v in node.attrib.items()} for node in model.iter('mesh')]
    if not repairs or any(any(i.values()) or set(i)!={'edges_fixed','degenerate_facets','facets_removed','facets_reversed','backwards_edges'} for i in repairs):
        fail={'id':r['id'],'ok':False,'stage':'repair','repairs':repairs}
        write(result,fail);return fail
    source=base;expected=[];project_file=None
    if r['pauses']:
        project_folder=OUT/'PROYECTOS_PRUSA_PAUSAS';project_folder.mkdir(exist_ok=True)
        project_file=project_folder/(r['id']+'_'+r['name']+'_PAUSAS_V16.3mf')
        codes=ET.Element('custom_gcodes_per_print_z',bed_idx='0')
        for a in r['pauses']:
            z=round(a['pause_before_model_layer_one_based']*.2,6);expected.append(z)
            ET.SubElement(codes,'code',print_z=str(z),type='1',extruder='1',color='#FFFFFF',
                          extra='Insertar '+a['nut_size']+': '+', '.join(a['insert_names']),gcode='')
        ET.SubElement(codes,'mode',value='SingleExtruder')
        contents[PAUSE_XML]=ET.tostring(codes,encoding='utf-8',xml_declaration=True)
        for node in model.iter('metadata'):
            if node.attrib.get('key')=='name':node.set('value',r['name'])
        contents[MODEL_XML]=ET.tostring(model,encoding='utf-8',xml_declaration=True)
        contents['Metadata/V16_PROCESO.txt']='0.4 mm; capas 0.20 mm incluida la primera; sin balsa; soporte desde cama; sin soportar puentes; separación superior 0.25 mm. Seleccionar el perfil real y probar la pausa de la máquina.\n'.encode()
        with ZipFile(project_file,'w',ZIP_DEFLATED,compresslevel=6) as z:
            for name,data in contents.items():z.writestr(name,data)
        source=project_file
    cmd=[str(SLICER),'--export-gcode','--threads','2',*bed,'--nozzle-diameter','0.4',
         '--layer-height',str(options['layer_height_mm']),'--first-layer-height',str(options['first_layer_height_mm']),
         '--perimeters',str(options['perimeters']),'--fill-density',str(options['infill_percent'])+'%',
         '--fill-pattern','gyroid','--perimeter-generator','arachne','--support-material','--support-material-auto',
         '--support-material-threshold','45','--support-material-contact-distance','0.25','--brim-width','5',
         '--raft-layers',str(options['raft_layers']),'--bed-shape','0x0,200x0,200x200,0x200',
         '--temperature','0','--first-layer-temperature','0','--bed-temperature','0','--first-layer-bed-temperature','0']
    if r['pauses']:
        cmd+=['--dont-support-bridges','--support-material-buildplate-only','--pause-print-gcode',';V16_PAUSA_DIAGNOSTICO']
    pr=subprocess.run([*cmd,'--output',str(out),str(source)],capture_output=True,text=True,timeout=260)
    (p/'laminado.log').write_text(pr.stdout+'\n'+pr.stderr,encoding='utf-8')
    measured=[];z=None
    if pr.returncode==0 and out.is_file():
        with out.open(encoding='utf-8') as stream:
            for line in stream:
                if line.startswith(';Z:'):z=float(line[3:])
                elif line.strip()==';V16_PAUSA_DIAGNOSTICO':measured.append(z)
        met=paths(out)
    else:met={}
    ok=bool(met.get('model_layers')) and expected==measured
    doc={'id':r['id'],'key':key,'stl_sha256':r['sha256'],'ok':ok,'slicer_exit':pr.returncode,
         'repairs':repairs,'pause_expected':expected,'pause_actual':measured,'config':options,**met}
    if project_file:doc['project_sha256']=sha(project_file)
    write(result,doc)
    print(r['id'],'PASS' if ok else 'ERROR','layers',met.get('model_layers'),'support/model',round(met.get('support_to_model_ratio') or 0,3),flush=True)
    return doc

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--assemble',action='store_true');cli.add_argument('--slice',action='store_true')
    cli.add_argument('--ids',nargs='+');a=cli.parse_args()
    rows=assemble() if a.assemble else read(OUT/'MANIFIESTO_STL_V16.json')['parts']
    if a.slice:
        selected=[r for r in rows if not a.ids or r['id'] in a.ids]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:res=list(pool.map(check_slicer,selected))
        for i,q in enumerate(res):
            if not q['ok']:res[i]=check_slicer(selected[i],always=True)
        f=OUT/'VERIFICACION_LAMINADO_V16.json' if not a.ids else DIAG/'VERIFICACION_PARCIAL.json'
        write(f,{'slicer':'PrusaSlicer 2.9.6','scope':'Diagnóstico de trayectorias a temperaturas 0; no es G-code de impresión.',
                 'passed':sum(x['ok'] for x in res),'total':len(res),'parts':res,'physical_print_verified':False})
        if not all(x['ok'] for x in res):raise SystemExit(2)

if __name__=='__main__':main()
