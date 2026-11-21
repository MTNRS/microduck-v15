from pathlib import Path
import sys,tempfile
t=Path(tempfile.gettempdir());sys.path.insert(0,str(t))
from md16_fit import *
k=('P36','P38','MG09_brazo_original_recortado','MG09_cubo_estriado_de_referencia','MG09_tornillo_original','Casquillo_igus_GSM_0405_04')
jaw=union(*(active[n] for n in k));tr=tree(jaw);verts,_,_=tr
amax=np.linalg.norm(verts[:,[0,2]]-pivot[[0,2]],axis=1).max();lo,hi=vec(jaw);rotation_deduction=2*amax*math.sin(math.radians(.25)/4)
g=Path('microduck-v16/V16_R1_G10_Ensayo_de_cassette');j=load(g/'Tendido_15_motores_en_ensayo.json');angles=np.arange(0,22.001,.25);rots=[rot(-a) for a in angles];cap=2.5;rows={}
for w in j['hilos']:
 p=dense(np.array(w['closed']),.19);r=w['od']/2;extra=r+.10+rotation_deduction;cut=cap+extra;mask=(p[:,1]>lo[1]-cut)&(p[:,1]<hi[1]+cut)&(np.linalg.norm(p[:,[0,2]]-pivot[[0,2]],axis=1)<=amax+cut);p=p[mask];best=cap;where=None
 for deg,m in zip(angles,rots):
  if not len(p):break
  xyz=p@m[:,:3].T+m[:,3];sel=np.all((xyz>=lo-cut)&(xyz<=hi+cut),axis=1)
  if not sel.any():continue
  d=sd(tr,xyz[sel])-extra;i=d.argmin()
  if d[i]<best:best=float(d[i]);where=[float(deg),p[sel][i].round(4).tolist()]
 rows[w['id']]={'cota_inferior_mm':float(np.floor(best*10000)/10000),'pose_y_punto':where}
out={'intervalo_grados':[0,22],'paso':.25,'conductores':len(rows),'radio_exterior_sobre_eje_mm':float(amax),'deduccion_rotacion_mm':float(rotation_deduction),'deduccion_entre_muestras_mm':.10,'umbral_de_informe_mm':cap,'piezas_moviles':k,'incidencias':{n:v for n,v in rows.items() if v['cota_inferior_mm']<0},'proximidades':rows}
save(g/'Verificacion/Barrido_153_ante_la_boca.json',out);print('boca',len(rows),out['incidencias'],min((d['cota_inferior_mm'],n) for n,d in rows.items()),flush=True)
