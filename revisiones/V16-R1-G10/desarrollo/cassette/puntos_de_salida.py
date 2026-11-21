from recolocar import *
def get(m):
 ns=[f'OEM{m:02}-{k}' for k in (1,2,3)];tips=np.array([wires[n]['closed'][-1] for n in ns]);k0=[];lo=tips.min(0)-3.;hi=tips.max(0)+3
 for k,(a,b) in rb.items():
  if np.all(a<hi)&np.all(b>lo):
   ds,gr=measure(k,tips,.625)
   if ds.min()<1.5:k0.append((k,np.round(ds,3).tolist(),np.round(gr[1],2).tolist()))
 print(m,k0,flush=True)
for m in (3,8,14,9,7,6,4,5):get(m)
