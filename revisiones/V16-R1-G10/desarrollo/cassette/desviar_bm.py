"""Shape the BM lead away from the component band while keeping both solder joints and the case."""
from recolocar import *
from medir_pads import signed_box
from itertools import product
from scipy.interpolate import CubicSpline
def assemble():
 n='W003';w=wires[n];q=np.array(w['closed'])[::-1];s=arc(q);tip=q[0];r=w['od']/2
 body=np.array([[-66.556,-26.,130.9],[-46.556,20.,132.3]]);middle=np.array([[-66.556,-21.8,130.9],[-46.556,15.,134.5]])
 bblo=tip-[11,7,4];bbhi=tip+[3,14,6]
 keys=[k for k,(lo,hi) in {**rb,**wb}.items() if k not in (n,'V15_PCM_250040_MAX') and np.all(lo<bbhi)&np.all(hi>bblo)]
 for k in ('P86','barrido_horizontal','barrido_vertical'): 
  if k in keys:raise ValueError(k)
 cand=[];t=np.linspace(0,1,86)[:,None]
 for endlen in (8,9,10,11,12,14,16):
  k=int(np.searchsorted(s,endlen));b=q[k];tb=unit((q[k+1]-q[k])[None,:])[0]
  for dx,dy,dz,dist in product((2.5,4,5.5,7,8.5),(-3,-1,0,1,2),(0,.4,1,2),(1.5,3,5)):
   a=tip+[-dx,dy,dz];c=b-tb*dist
   pp=(1-t)**3*tip+3*t*(1-t)**2*a+3*t**2*(1-t)*c+t**3*b
   ss=arc(pp);dirs=unit(np.diff(pp,axis=0));ag=np.arccos(np.clip(np.sum(dirs[:-1]*dirs[1:],axis=1),-1,1));rad=(np.minimum(np.diff(ss)[1:],np.diff(ss)[:-1])/np.maximum(ag,1.e-6)).min()
   if rad<1.9:continue
   band=(signed_box(pp,*middle)-r).min()
   lam=(signed_box(pp,*body)-r).min()
   if band<.37 or lam<.1:continue
   cand.append((pp,k,rad,band,lam,ss[-1]))
 if not cand:print('sin curva geometrica');return
 arr=np.stack([x[0] for x in cand]);flat=arr.reshape(-1,3);mg=np.full(len(flat),8.);los={};tol=np.max(np.linalg.norm(np.diff(arr,axis=1),axis=-1),axis=1)/2
 for key in keys:
  ds,_=measure(key,flat,r);ds=ds.reshape(len(arr),-1);los[key]=ds.min(1)-tol
  if key!='P45':mg=np.minimum(mg,ds.ravel())
 free=mg.reshape(len(arr),-1).min(1)-tol
 for minallow in (.33,.23,.15):
  opts=np.flatnonzero(free>=minallow)
  if len(opts):break
 if not len(opts):
  i=int(free.argmax());print('mejor sin paso',free[i],sorted((round(v[i],3),k) for k,v in los.items())[:6]);return
 i=max(opts,key=lambda i:min(.65,free[i])+.10*min(4,cand[i][2])+.09*min(2,cand[i][3])+.9*min(0,los['P45'][i]))
 p,k,rmin,c,l,length=cand[i];f=np.vstack((p,q[k+1:]))[::-1]
 assert np.allclose(f[[0,-1]],np.array(w['closed'])[[0,-1]])
 w.update(closed=f.round(6).tolist(),opened=f.round(6).tolist(),longitud_trazada_mm=round(float(arc(f)[-1]),3))
 out={'etiqueta':tag,'anclajes_conservados':True,'ramal':n,'hasta_empalme_con_recorrido_anterior_mm':float(s[k]),'tramo_nuevo_mm':float(length),'radio_curvatura_aprox_mm':float(rmin),'margen_a_reserva_central_mm':float(c-tol[i]),'margen_al_laminado_mm':float(l-tol[i]),'margen_inferior_otros_vecinos_mm':float(free[i]),'vecinos':{key:round(float(d[i]),4) for key,d in los.items() if d[i]<3},'tramo':p.round(6).tolist()}
 save(jdir/(tag+'.json'),j);save(dest/'BM_desvio_junto_al_pad.json',out);print({k:v for k,v in out.items() if k!='tramo'})
if __name__=='__main__':assemble()
