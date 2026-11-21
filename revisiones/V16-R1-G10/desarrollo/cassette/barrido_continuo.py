from rebaje_tapa import *
sys.path[:0]=[str(T/'md17audbm'),str(T)];from perfil_terminales import sampled_profile
def arrayw(tag,step):
 js=json.loads((r/'trabajo/arnes_polaridad/arnes_15_motores'/(tag+'.json')).read_text('utf8'))
 ids=[];qa=[];rr=[];names=[]
 for i,w in enumerate(js['hilos']):
  q,rad=sampled_profile(w,step);ids.extend([i]*len(q));qa.extend(q);rr.extend(rad);names.append(w['id'])
 return names,np.asarray(ids),np.asarray(qa),np.asarray(rr)
def evaluate(poses,g,pre,grain=.075,cap=.90):
 names,ids,p,rad=pre;v,f=verts(g);vmin=v.min(0);vmax=v.max(0);tr=igl.AABB();tr.init(v,f);results=[];summary={};w_step=.14
 for a,b in zip(np.array(poses,float),np.array(poses[1:],float)):
  shift=b-a;L=np.linalg.norm(shift);unit=shift/L;marg=cap+rad.max()+w_step/2+grain
  low=vmin+np.minimum(a,b)-marg;hi=vmax+np.maximum(a,b)+marg;sel=np.flatnonzero(np.all((p>=low)&(p<=hi),axis=1));q=p[sel]-a;rs=rad[sel];dd=np.full(len(q),cap);pose_at=np.zeros(len(q));count=[0]
  def recur(I,t,reach):
   pt=q[I]-t*unit
   mask=np.all((pt>=vmin-marg-reach)&(pt<=vmax+marg+reach),axis=1)
   I=I[mask];pt=pt[mask]
   if not len(I):return
   sq,_,_=tr.squared_distance(v,f,pt);ds=np.sqrt(sq);inside=np.all((pt>=vmin)&(pt<=vmax),axis=1)
   if inside.any():ds[inside]*=np.where(abs(igl.fast_winding_number(v,f,pt[inside]))>.5,-1,1)
   d=ds-rs[I]-.5*w_step-reach;count[0]+=len(I);test=d<dd[I]
   if not test.any():return
   if reach<=grain:
    K=I[test];dd[K]=d[test];pose_at[K]=t;return
   K=I[test];recur(K,t-reach*.5,reach*.5);recur(K,t+reach*.5,reach*.5)
  for lo in np.arange(0,L,3.):
   hh=min(lo+3.,L);recur(np.arange(len(q)),(lo+hh)*.5,(hh-lo)*.5)
  h={}
  for wi in set(ids[sel][dd<cap]):
   kk=np.flatnonzero(ids[sel]==wi);k=kk[dd[kk].argmin()];h[names[wi]]=dict(mm=round(float(dd[k]),4),punto=p[sel[k]].round(3).tolist(),desplazamiento_tapa=(a+unit*pose_at[k]).round(3).tolist())
  results.append(dict(desde=a.tolist(),hasta=b.tolist(),proximidades=h,consultas=count[0]));print(b.tolist(),min([(v['mm'],k) for k,v in h.items()] or [(cap,None)]),flush=True)
  for k,x in h.items():
   if k not in summary or x['mm']<summary[k]['mm']:summary[k]=x
 return dict(metodo='Malla real de P86 en movimiento continuo. Distancias con radio local del conductor y mitad del paso máximo de 0,14 mm deducidos. Cada intervalo de traslación resta además su semilongitud por la cota de Lipschitz.',paso_max_muestreo_mm=w_step,semilongitud_terminal_maxima_mm=grain,umbral_informe_mm=cap,numero_conductores=len(names),tramos=results,cota_inferior=min([x['mm'] for x in summary.values()] or [cap]),proximidades=summary)
if __name__=='__main__':
 folder=here;lr=geom(folder/'P86_alivio_interior.npz');tag=sys.argv[1];pre=arrayw(tag,.14)
 paths={'recta_original':[[-90,0,12],[0,0,12],[0,0,0]],'oblicua':[[-90,0,14],[-18,0,14],[0,0,8],[0,0,0]],'oblicua_larga':[[-90,0,14],[-37,0,14],[0,0,7],[0,0,0]],'escalon':[[-90,0,14],[-12,0,14],[-12,0,8],[0,0,8],[0,0,0]]}
 paths.update({f'entrada_{h}':[[-90,0,14],[-18,0,14],[0,0,h],[0,0,0]] for h in (9,10,11)})
 for key in sys.argv[2:]:
  print(key,flush=True);x=evaluate(paths[key],lr,pre);(folder/(tag+'_barrido_'+key+'.json')).write_text(json.dumps(x,indent=1),'utf8')
