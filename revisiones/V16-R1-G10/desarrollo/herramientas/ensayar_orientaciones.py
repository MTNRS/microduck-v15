from pathlib import Path
import argparse,concurrent.futures,json,subprocess
import numpy as np
from auditar_impresion import ROOT,V15,load_facets,paths,surface_stats

SLICER=Path('C:/microduck-tools/PrusaSlicer-2.9.6/PrusaSlicer-2.9.6/prusa-slicer-console.exe')
WORK=ROOT/'trabajo'/'orientaciones-mecanica'

def transform(facets,matrix):
    return (facets.astype(np.float64) @ matrix[:3,:3].T+matrix[:3,3]).astype(np.float32)

def binary_stl(path,facets):
    record=np.zeros(len(facets),dtype=[('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')])
    v=facets.astype(np.float64)
    normals=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0])
    lengths=np.linalg.norm(normals,axis=1)
    if np.any(lengths==0):raise ValueError('Triángulo degenerado tras la transformación')
    record['normal']=normals/lengths[:,None];record['vertices']=facets
    with path.open('wb') as out:
        out.write(b'Microduck V16 STL mm'.ljust(80,b' '));out.write(len(facets).to_bytes(4,'little'));out.write(record.tobytes())

def measure(facets,R):
    q=facets.astype(np.float64)@R.T
    T=np.eye(4);T[:3,:3]=R;T[:3,3]=-q.reshape(-1,3).min(axis=0)
    q+=T[:3,3]
    n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);a=np.linalg.norm(n,axis=1)
    z=q[:,:,2];down=n[:,2]/a
    bottom=(z.max(axis=1)<.01)&(down<-.99)
    footprint=float((a[bottom]/2).sum())
    exposed=(down<-.707)&(z.mean(axis=1)>.3)
    support=float((-n[exposed,2]/2).sum())
    return dict(matrix=T.tolist(),flat_contact_mm2=footprint,underside_projection_proxy_mm2=support,height_mm=float(z.max()))

def candidates(facets):
    choices=[]
    for i,up in enumerate(np.vstack([np.eye(3),-np.eye(3)])):
        x=np.eye(3)[np.argmin(abs(up))];R=np.vstack([x,np.cross(up,x),up])
        choices.append({'axis':('X','Y','Z','-X','-Y','-Z')[i],**measure(facets,R)})
    # Screen for actual flat contact. Retain stable bottom faces plus a short,
    # lower-overhang trial. Select from actual toolpath results afterward.
    by_contact=sorted(choices,key=lambda r:(-r['flat_contact_mm2'],r['underside_projection_proxy_mm2']))
    by_support=sorted(choices,key=lambda r:(r['underside_projection_proxy_mm2'],r['height_mm']))
    result={}
    for r in [*by_contact[:2],*by_support[:2]]:result[r['axis']]=r
    return choices,list(result.values())

def run(job):
    row, trial, base=job
    dest=WORK/(row['id']+'_'+trial['axis'])
    dest.mkdir(exist_ok=True,parents=True)
    stl=dest/'trial.stl';out=dest/'diagnostico.gcode'
    f=transform(base,np.array(trial['matrix']))
    check=surface_stats(f)
    bad=('zero_area','duplicate_faces','edges_not_two','inconsistent_edges')
    if any(check[k] for k in bad):
        # A signed axis permutation preserves float32 bit positions. Moving
        # the part to the bed belongs to the slicer, without rebaking XYZ.
        matrix=np.array(trial['matrix']);matrix[:3,3]=0
        trial={**trial,'matrix':matrix.tolist(),'slicer_drop_to_bed':True}
        f=transform(base,matrix)
        check=surface_stats(f)
        if any(check[k] for k in bad):
            return {**trial,'id':row['id'],'ok':False,'topology':check}
    binary_stl(stl,f)
    cmd=[str(SLICER),'--export-gcode','--threads','2','--nozzle-diameter','0.4','--layer-height','0.2','--first-layer-height','0.2',
         '--filament-diameter','1.75','--perimeters',str(row['perimeters']),'--fill-density',str(row['infill_percent'])+'%',
         '--fill-pattern','gyroid','--support-material','--support-material-auto','--support-material-threshold','45',
         '--support-material-contact-distance','0.25','--brim-width','5','--raft-layers','0','--bed-shape','0x0,200x0,200x200,0x200',
         '--center','100,100','--temperature','0','--first-layer-temperature','0','--bed-temperature','0',
         '--first-layer-bed-temperature','0','--output',str(out),str(stl)]
    res=subprocess.run(cmd,capture_output=True,text=True,timeout=200)
    (dest/'laminador.log').write_text(res.stdout+'\n'+res.stderr,encoding='utf-8')
    met=paths(out) if res.returncode==0 and out.is_file() else {}
    record={**trial,'id':row['id'],'ok':bool(met and met['model_layers']),'slicer_exit':res.returncode,
            'stl':str(stl),**met}
    (dest/'resultado.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(row['id'],trial['axis'],'contact',round(trial['flat_contact_mm2'],1),'support/model',round(record.get('support_to_model_ratio') or 0,3),record['ok'],flush=True)
    return record

def main():
    ap=argparse.ArgumentParser();ap.add_argument('ids',nargs='+');args=ap.parse_args()
    WORK.mkdir(exist_ok=True,parents=True)
    m=json.loads((V15/'STL_MANIFIESTO_V15.json').read_text(encoding='utf-8'))
    jobs=[];selection={}
    for r in m['parts']:
        if r['id'] not in args.ids:continue
        if r['orientation'].get('required_pauses'):raise ValueError('No rotar pieza con pausas')
        base=load_facets(V15/r['file'].replace('\\','/'))
        all_rows,chosen=candidates(base);selection[r['id']]=all_rows
        for c in chosen:jobs.append((r,c,base))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(run,jobs))
    (WORK/'ENSAYOS.json').write_text(json.dumps({'axis_screen':selection,'sliced':out},indent=2),encoding='utf-8')
if __name__=='__main__':main()
