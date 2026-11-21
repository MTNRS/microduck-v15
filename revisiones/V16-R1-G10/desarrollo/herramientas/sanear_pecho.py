from pathlib import Path
import json
import numpy as np
import trimesh
import manifold3d as mf
from auditar_impresion import ROOT,V15,load_facets,surface_stats,sha
from ensayar_orientaciones import binary_stl

OUT=ROOT/'trabajo'/'pecho'
OUT.mkdir(exist_ok=True,parents=True)
row=next(r for r in json.loads((V15/'STL_MANIFIESTO_V15.json').read_text(encoding='utf-8'))['parts'] if r['id']=='P44')
source=V15/row['file'].replace('\\','/')
assert sha(source)==row['sha256']
a=load_facets(source)
stats=surface_stats(a)
vertices,idx=np.unique(a.reshape(-1,3),axis=0,return_inverse=True)
f=idx.reshape(-1,3)
raw=mf.Manifold(mf.Mesh64(np.ascontiguousarray(vertices,dtype=np.float64),np.ascontiguousarray(f,dtype=np.uint64)))
assert raw.status()==mf.Error.NoError and len(raw.decompose())==1
old=trimesh.Trimesh(vertices,f,process=False)
def retriangulate_exact_collinear(v, f):
    # A collinear facet spans one long edge and its two subdivisions. The
    # adjacent facet on the long edge can absorb the middle vertex exactly.
    faces=[list(map(int,x)) for x in f]
    repaired=0
    while True:
        ids=[i for i,x in enumerate(faces) if x is not None]
        tri=v[np.asarray([faces[i] for i in ids])].astype(float)
        flat=np.flatnonzero(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)==0)
        if not len(flat):
            return np.asarray([faces[i] for i in ids]),repaired
        i=ids[int(flat[0])]
        a,b,c=faces[i]
        _,end1,end2,mid=max((float(np.linalg.norm(v[x].astype(float)-v[y])),x,y,z)
                            for x,y,z in ((a,b,c),(b,c,a),(c,a,b)))
        if len({a,b,c})!=3:
            raise ValueError('Collapsed rather than collinear')
        neighbors=[j for j in ids if j!=i and end1 in faces[j] and end2 in faces[j]]
        if len(neighbors)!=1:
            raise ValueError('Unexpected long-edge adjacency')
        j=neighbors[0];cyc=faces[j]
        for k in range(3):
            x,y,z=cyc[k],cyc[(k+1)%3],cyc[(k+2)%3]
            if {x,y}=={end1,end2}:
                faces[j]=[x,mid,z];faces.append([mid,y,z]);faces[i]=None
                break
        repaired+=1
        if repaired>100:raise ValueError('Collinear cleanup did not converge')

results=[]
for tol in (.00025,.0005,.001,.0015,.002,.005):
    simpl=raw.simplify(tol)
    if simpl.status()!=mf.Error.NoError or len(simpl.decompose())!=1:
        print(tol,'rechazada componentes',len(simpl.decompose()),str(simpl.status()),flush=True)
        continue
    mesh=simpl.to_mesh64()
    nv=np.array(mesh.vert_properties,dtype=np.float32)[:,:3]
    nf=np.array(mesh.tri_verts)
    try:
        nf,repairs=retriangulate_exact_collinear(nv,nf)
    except ValueError as e:
        print(tol,str(e),flush=True);continue
    b=nv[nf]
    s=surface_stats(b)
    bounds=float(np.max(np.abs(np.array([a.min(axis=(0,1)),a.max(axis=(0,1))])-np.array([b.min(axis=(0,1)),b.max(axis=(0,1))]))))
    volume=s['signed_volume_mm3']-stats['signed_volume_mm3']
    result={'tolerance_mm':tol,'exact_collinear_retriangulated':repairs,'bounds_delta_mm':bounds,'volume_delta_mm3':volume,**s}
    if not any(s[k] for k in ('zero_area','duplicate_faces','edges_not_two','inconsistent_edges')) and bounds<.005 and abs(volume)<.5:
        new=trimesh.Trimesh(nv,nf,process=False)
        rng=np.random.default_rng(16044)
        distances=[]
        for src,other in ((old,new),(new,old)):
            index=rng.choice(len(src.faces),size=1024,replace=False)
            pts=np.vstack([src.triangles_center[index],src.triangles[index,0]])
            distance=trimesh.proximity.closest_point(other,pts)[1]
            distances.append(float(np.max(distance)))
        result['sampled_surface_max_mm_both_directions']=distances
        if max(distances)<=tol+.00002:
            name='P44_SANEADO_'+str(tol).replace('.','p')+'.stl'
            binary_stl(OUT/name,b)
            result.update(file=name,sha256=sha(OUT/name),accepted=True)
    results.append(result)
    print(tol,s['facets'],s['slivers_quality_below_0p001'],'area tiny',s['tiny_area_below_1e_6_mm2'],
          'bounds',bounds,'volume',volume,'bad',{k:s[k] for k in ('zero_area','duplicate_faces','edges_not_two','inconsistent_edges')},'distances',result.get('sampled_surface_max_mm_both_directions'),'accepted',result.get('accepted'),flush=True)
(OUT/'SANEADO_P44.json').write_text(json.dumps({'source':row['sha256'],'baseline':stats,'candidates':results},indent=2),encoding='utf-8')
