from recolocar import *
def go(m):
 ns=[f'OEM{m:02}-{k}' for k in (1,2,3)];tips=np.array([wires[n]['closed'][-1] for n in ns]);k=f'V7_SRC_V4_MD_{m:02}_MG90S_CUERPO';norm=measure(k,tips,.625)[1][1];out={}
 for L in (0,1,2,3,4,6,8):
  xyz=tips+L*norm;low=xyz.min(0)-2;hi=xyz.max(0)+2
  items=sorted([(float(measure(kk,xyz,.625)[0].min()),kk) for kk,(a,b) in {**rb,**wb}.items() if kk!=k and kk not in ns and np.all(a<hi)&np.all(b>low)]);out[str(L)]=items[:3]
 print('goma',m,[(l,v[0] if v else None) for l,v in out.items()],flush=True)
for m in (3,14,8,9,6,7,4,5):go(m)
