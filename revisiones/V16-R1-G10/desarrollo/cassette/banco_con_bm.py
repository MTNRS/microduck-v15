from canal_bm_p45 import *
from recolocar import geom as bodies, vec, jdir, j as original_harness
g=r/'V16_R1_G10_Ensayo_de_cassette';v=g/'Verificacion';kit=r/'V16_R1_G10_Ensayo_P45'
def read(f):return json.loads(f.read_text('utf-8-sig'))
def store(f,d):f.write_text(json.dumps(d,indent=1,ensure_ascii=False),'utf8')
source=read(jdir/'Tendido_G10_cassette.json');s0=read(here/'BM_desvio_junto_al_pad.json');q=np.array(s0['tramo']);wire=next(w for w in source['hilos'] if w['id']=='W003');assert np.max(abs(np.array(wire['closed'])[-len(q):][::-1]-q))<1.e-5
d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];src=source['salidas_PCM']['BM'];src.update(trazado_mm=q.tolist(),distancias_sobre_trazado_mm=d.round(5).tolist());source['estado']='Ensayo de cassette G10. Pendiente resolver interferencias globales del arnés.'
store(g/'Tendido_15_motores_en_ensayo.json',source)
p45=geom(here/'P45_BM_canal_sin_isla.npz');sw=geom(here/'BM_barrido_de_entrada.npz');pose=mk(q,.55,np.array([[0,0,0],[0,0,0]]));bodies['P45']=p45;out={}
def inspect(m,solids):
 l,u=vec(m);rec={}
 for k,b in solids.items():
  a,c=vec(b)
  if np.any(a>u+4) or np.any(c<l-4):continue
  rec[k]={'holgura_mm':round(m.min_gap(b,4),5),'interseccion_mm3':round((m^b).volume(),7)}
 return rec
stage1={k:b for k,b in bodies.items() if k=='P45' or 'FUSE' in k or 'MINI' in k}
stage2={k:b for k,b in bodies.items() if k in ('P83','P63','P66','P67') or any(w in k for w in ('REED','Reed','BALANCE','_BM_'))}
out['entrada_placa_en_cassette']=inspect(sw,stage1)
out['presentacion_de_P83']=inspect(mk(q,.55,np.array([[0,0,0],[0,-68,0]])),stage2)
out['entrada_de_P65']=inspect(mk(q,.55,np.array([[0,0,0],[0,0,22.]])),{'P65':bodies['P65']})
out['asiento_con_otros_solidos']=inspect(pose,{k:b for k,b in bodies.items() if k!='V15_PCM_250040_MAX'})
store(v/'Entrada_con_cable_BM_formado.json',out);print({step:{k:x for k,x in vv.items() if x['interseccion_mm3']>1.e-6} for step,vv in out.items()})
print([(name,min((x['holgura_mm'],k) for k,x in vv.items()) if vv else None) for name,vv in out.items()])
