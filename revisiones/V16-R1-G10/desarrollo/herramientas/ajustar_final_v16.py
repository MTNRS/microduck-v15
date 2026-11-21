from pathlib import Path
import argparse,csv,shutil,struct
import numpy as np

from preparar_v16 import OUT,WORK,read,write,check_slicer,GEOMETRY_KEYS
from auditar_impresion import load_facets,surface_stats,sha
from ensayar_orientaciones import binary_stl

def update_list(rows):
    file=OUT/'LISTA_IMPRESION_V16.csv'
    fields=['id','name','file','color','material','quantity','layer_height_mm','first_layer_height_mm','perimeters',
            'infill_percent','brim_mm','raft_layers','support_top_gap_mm','supports_only_from_buildplate','pauses','motivo']
    with file.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({**r,**r['process'],'pauses':len(r['pauses'])})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--p45',action='store_true')
    parser.add_argument('--p44',type=Path)
    a=parser.parse_args()
    manifest=read(OUT/'MANIFIESTO_STL_V16.json')
    verify=read(OUT/'VERIFICACION_LAMINADO_V16.json')
    assert verify['passed']==verify['total']==80
    rows=manifest['parts'];old={r['id']:r for r in verify['parts']};new=[]
    if a.p45:
        r=next(x for x in rows if x['id']=='P45')
        r['process'].update(layer_height_mm=.1,first_layer_height_mm=.1)
        r['motivo']='Capas de 0,10 mm para el labio de la escotilla y dos microcavidades internas eliminadas'
        new.append(r)
    if a.p44:
        r=next(x for x in rows if x['id']=='P44')
        assert r['process']['layer_height_mm']==.2 and len(r['pauses'])==2
        base=OUT/r['file']
        before=load_facets(base);candidate=load_facets(a.p44)
        s=surface_stats(candidate)
        assert not any(s[k] for k in GEOMETRY_KEYS)
        assert np.max(np.abs(np.array([before.min(axis=(0,1)),before.max(axis=(0,1))])
                             -np.array([candidate.min(axis=(0,1)),candidate.max(axis=(0,1))])))<.006
        assert abs(s['signed_volume_mm3']-r['signed_volume_mm3'])<12
        raw=a.p44.read_bytes()
        assert len(raw)==84+50*struct.unpack_from('<I',raw,80)[0]
        csg=read(a.p44.parent/'P44_ALIVIO_CAP06_QA.json')
        assert csg['output_STL_sha256']==sha(a.p44)
        assert max(csg['removed_stock_in_protected_guards_mm3'].values())<.001
        shutil.copyfile(a.p44,base)
        assert np.array_equal(load_facets(base),candidate)
        r.update(**s,sha256=sha(base),mesh_changed=True,adjustment_input_sha256=sha(a.p44),
                 motivo='Bisel local en la abertura CAP06. Conserva los alojamientos y las pausas de 45 y 46 mm')
        new.append(r)
    assert new
    for r in new:
        q=check_slicer(r,always=True)
        if not q['ok']:
            q=check_slicer(r,always=True)
        if not q['ok']:raise SystemExit(2)
        old[r['id']]=q
    verify['parts']=[old[r['id']] for r in rows]
    write(OUT/'VERIFICACION_LAMINADO_V16.json',verify)
    write(OUT/'MANIFIESTO_STL_V16.json',manifest)
    update_list(rows)
    print('VALIDADOS AJUSTES',','.join(r['id'] for r in new),flush=True)
if __name__=='__main__':main()
