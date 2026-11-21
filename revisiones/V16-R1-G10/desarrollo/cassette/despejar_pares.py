from recolocar import *
from scipy.linalg import block_diag
from scipy.spatial.distance import cdist
GDIR=Path(__file__).parent
for key,f in {'P86':'P86_alivio_interior','barrido_vertical':'barrido_bajada_G9','barrido_horizontal':'barrido_entrada_G9'}.items():
 geom[key]=readg(GDIR/(f+'.npz'));rb[key]=vec(geom[key]);cache.pop(key,None)
def hull(name,nearest,wide):
 w=wires[name];orig=np.array(w['closed']);full=dense(orig,.29);sfull=arc(full);idx=np.linalg.norm(full-nearest,axis=1).argmin();ln=sfull[idx]
 if w.get('curva_preformada_terminal') or w.get('terminal_placa_plantar'):return
 term=.95 if name.startswith('OEM') else 1.30
 if w.get('terminal_PCM'):term=10.3
 ii=np.flatnonzero((sfull>=max(term,ln-wide))&(sfull<=min(ln+wide,sfull[-1]-term)))
 if len(ii)<4:return
 p=full[ii];s=sfull[ii];width=s[-1]-s[0];anchors=np.linspace(s[0],s[-1],max(6,min(10,int(width/2.7)+2)));B=CubicSpline(anchors,np.eye(len(anchors)),axis=0,bc_type='clamped')(s)[:,1:-1];nc=B.shape[1]
 return dict(name=name,p=p,B=B,nc=nc,r=w['od']/2,c=np.zeros((nc,3)),s=s,orig=orig,q=p,pre=full[:ii[0]],post=full[ii[-1]+1:])
def solve(u,v):
 aa=wt[u].data;ds,inds=wt[v].query(aa);k=int(ds.argmin());start=aa[k];end=wt[v].data[inds[k]];limit=wires[u]['od']/2+wires[v]['od']/2
 if ds[k]>=limit+.02:return
 parts=[hull(u,start,10.),hull(v,end,10.)]
 if any(x is None for x in parts):return
 total=sum(p['nc']*3 for p in parts)
 regs=[];off=0
 for x in parts:
  nm=x['name'];p=x['p'];x['slice']=slice(off,off+x['nc']*3);off+=x['nc']*3;low=p.min(0)-3.7;hi=p.max(0)+3.7
  keys=[k for k,(l,h) in {**rb,**wb}.items() if k not in (u,v) and np.all(l<hi)&np.all(h>low)]
  basev={k:measure(k,p,x['r'])[0] for k in keys};x['base']={k:a for k,a in basev.items() if min(a)<2.4}
  d2=np.diff(np.eye(x['nc']+2),n=2,axis=0)[:,1:-1];regs.append(np.kron(.07*np.eye(x['nc'])+.13*d2.T@d2,np.eye(3)))
 A,C=parts
 reg=block_diag(*regs);cf=np.zeros(total)
 def pose(cf):
  for x in parts:x['q']=x['p']+x['B']@cf[x['slice']].reshape(-1,3)
 def constrain():
  errors=[];grads=[];wg=[]
  for x in parts:
   for key,before in x['base'].items():
    ds,gs=measure(key,x['q'],x['r']);threshold=np.minimum(.27,before-.004)
    sel=np.flatnonzero(threshold-ds>-.48)
    if not len(sel):continue
    err=threshold[sel]-ds[sel];jac=np.zeros((len(sel),total));jac[:,x['slice']]=(x['B'][sel,:,None]*gs[sel,None,:]).reshape(len(sel),-1)
    errors.extend(err);grads.extend(jac);wg.extend([20]*len(sel))
  dis=cdist(A['q'],C['q']);ia,ib=np.where(dis<limit+.55)
  if len(ia):
   g=unit(A['q'][ia]-C['q'][ib])
   jac=np.zeros((len(ia),total))
   jac[:,A['slice']]=(g[:,None,:]*A['B'][ia,:,None]).reshape(len(ia),-1)
   jac[:,C['slice']]=(-g[:,None,:]*C['B'][ib,:,None]).reshape(len(ia),-1)
   errors.extend(limit+.20-dis[ia,ib]);grads.extend(jac);wg.extend([4.]*len(ia))
  return np.array(errors),np.array(grads),np.array(wg)
 for it in range(18):
  pose(cf);err,G,weights=constrain()
  if not len(err):break
  def cost(z):
   new=cf+z;pen=np.maximum(0,err-G@z);return float((weights*pen)@pen+new@reg@new+.08*z@z),-2*G.T@(weights*pen)+2*reg@new+.16*z
  res=minimize(cost,np.zeros(total),jac=True,bounds=[(-.23,.23)]*total,method='L-BFGS-B',options={'maxiter':42,'ftol':1.e-9});cf+=res.x
  if abs(res.x).max()<.003:break
 before=float(ds[k]-limit);best=None
 for frac in (1.,.87,.73,.6,.45,.32):
  pose(cf*frac);lost=False;fs=[]
  for x in parts:
   for key,b0 in x['base'].items():
    da=measure(key,x['q'],x['r'])[0]
    if (np.minimum(.23,b0)-da).max()>.035:lost=True;break
   if lost:break
   mask=(x['p'][:,2]>120)&(x['p'][:,2]<165)
   if mask.any():
    s0=sd(sskin,x['p'][mask]);s1=sd(sskin,x['q'][mask]);closed=s0<-.25
    if np.any(s1[closed]>np.maximum(-.15,s0[closed]+.45)):lost=True;break
   so=arc(x['orig']);s=x['s'];curve=np.vstack((x['orig'][so<s[0]-.000001],x['q'],x['orig'][so>s[-1]+.000001]));fs.append(curve)
  if lost:continue
  x,y=[dense(p,.13) for p in fs];after=cKDTree(x).query(y)[0].min()-limit
  if after>before+.06:best=(fs,after);break
 if best:
  fs,after=best
  for x,f in zip(parts,fs):
   n=x['name'];w=wires[n];w.update(closed=f.round(6).tolist(),opened=f.round(6).tolist(),longitud_trazada_mm=round(float(arc(f)[-1]),4));setup(n)
  save(jdir/(tag+'.json'),j);fp=GDIR/(tag+'_historia.json');records=load(fp) if fp.exists() else [];records.append(dict(par=[u,v],antes_mm=round(before,4),despues_mm=round(float(after),4)));save(fp,records);print('par',u,v,round(before,3),round(after,3),flush=True)
reports=load(root/'V16_R1_G9_Ensayo_de_cierre/Verificacion/Holguras_del_arnes_15_motores.json')
for pair,mag in sorted(reports['pares_de_aislamientos_solapados'].items(),key=lambda kv:-kv[1]):
 u,v=pair.split(' / ')
 try:solve(u,v)
 except Exception as exc:print('ERROR',u,v,str(exc),flush=True)
