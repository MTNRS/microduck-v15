"""Compare the five fitted PCM leads with the manufacturer's pad photograph in cassette coordinates."""
from prisma import geom,box,T,here,np,json,M
from pathlib import Path
import hashlib
import sys
import igl
board_size=np.array([46.,20.]);xmax=-46.556;ymax=20.
# Points on the four outer corners of the PCB in the embedded 220 px product photo.
corners=np.array([[26.5,74.0],[194.5,75.0],[193.5,147.5],[26.5,146.0]])
unit=np.array([[0.,0.],[1.,0.],[1.,1.],[0.,1.]])
mat=[];right=[]
for (u,v),(x,y) in zip(corners,unit):
 mat.extend([[u,v,1,0,0,0,-x*u,-x*v],[0,0,0,u,v,1,-y*u,-y*v]]);right.extend([x,y])
hom=np.r_[np.linalg.solve(mat,right),1.].reshape(3,3)
def world(px):
 uv=hom@np.r_[px,1];u,v=uv[:2]/uv[2];return np.array([xmax-20*v,ymax-46*u])
def signed_box(p,lo,hi):
 d=abs(p-(lo+hi)/2)-(hi-lo)/2
 return np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(np.max(d,axis=1),0)
def run():
 root=Path('microduck-v16');folder=Path(sys.argv[1]) if len(sys.argv)>1 else root/'V16_R1_G9_Ensayo_de_cierre';j=json.loads((folder/'Tendido_15_motores_en_ensayo.json').read_text('utf8'))
 bounds=np.array([[-66.556,-26.,130.9],[-46.556,20.,134.5]]);lam=bounds.copy();lam[1,2]=132.3
 # Reserve every point of the interior band up to max component height. 22-pixel end zones are visible on both short sides.
 # Deliberately use only 18.2 px (5 mm) on the B end and 15.3 px (4.2 mm) on the P end.
 central=bounds.copy();central[0,1]+=4.2;central[1,1]-=5.
 photo={'B+':[37.5,84.0],'B−':[37.5,135.0],'BM':[183.0,136.0],'P+':[182.2,86.8],'P−':[182.1,110.0]}
 leads={}
 for w in j['hilos']:
  pad=w.get('terminal_PCM')
  if not pad:continue
  q=np.array(w['closed']);ctr=world(photo[pad]);q=q if np.linalg.norm(q[0,:2]-ctr)<np.linalg.norm(q[-1,:2]-ctr) else q[::-1]
  s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];u=np.linspace(0,s[-1],int(np.ceil(s[-1]/.04))+1)
  strip=j['salidas_PCM'][pad]['distancia_pelado_mm']
  u=np.unique(np.r_[u,strip-1.e-6,strip])
  p=np.column_stack([np.interp(u,s,c) for c in q.T]);ins=w['od']/2;rad=np.where(u<strip,min(.75,ins),ins)
  lo=signed_box(p,*lam)-rad;mid=signed_box(p,*central)-rad;env=signed_box(p,*bounds)-rad;close=env<=0;ep=q[0,:2]
  def stats(d,rng):
   ids=np.where(rng)[0];i=ids[np.argmin(d[ids])]
   return dict(margen_inferior_mm=round(float(d[i]-.021),4),a_mm_del_pad=round(float(u[i]),3),centro_mundo_mm=p[i].round(4).tolist())
  leads[w['id']]=dict(pad=pad,centro_foto_xy_mm=ctr.round(3).tolist(),centro_CAD_xy_mm=ep.tolist(),distancia_centros_xy_mm=round(float(np.linalg.norm(ep-ctr)),3),pelado_modelado_mm=strip,laminado_tramo_pelado=stats(lo,u<strip),laminado_tramo_aislado=stats(lo,u>=strip),reserva_central=stats(mid,u>=0),intervalo_afectado_por_caja_completa_mm=[round(float(u[close].min()),3),round(float(u[close].max()),3)])
 doc=dict(fuente='https://mantech.co.za/datasheets/products/hx-2s-d20_250040.pdf',foto_px_cuatro_esquinas=corners.tolist(),centros_visuales_px=photo,hipotesis=dict(espesor_laminado_mm=1.4,banda_reservada_Y_mm=central[:,1].tolist(),paso_maximo_mm=.04,precision_foto_mm_por_pixel_aprox=.28),hilos=leads)
 output=folder/'Verificacion/Comprobacion_de_cinco_pads_PCM.json' if len(sys.argv)>1 else here/'PCM_hilos_frente_a_fotografia.json'
 print({n:v['reserva_central']['margen_inferior_mm'] for n,v in leads.items()});output.write_text(json.dumps(doc,indent=1,ensure_ascii=False),'utf8')
if __name__=='__main__':run()
