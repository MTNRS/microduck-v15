from pathlib import Path
here=Path(__file__).parent
exec(compile((here/'cierre_con_solidos.py').read_text('utf-8-sig').split('for n in sys.argv[1:]')[0],str(here/'cierre_con_solidos.py'),'exec'))
allg['P86']=g
for n in axes:allg[n]=get(n)
res={}
for n,(pt,ax) in axes.items():
 p=np.array(pt);a=np.array(ax);screw=get(n);toolset={'varilla':tub(p,a,.05,60,2.05),'mango':tub(p,a,50,190,14.1),'entrada_tornillo':M.batch_hull([screw,screw.translate((a*10).tolist())])}
 data={}
 for key,obj in toolset.items():
  l,u=vec(obj);mg=100;near0=None;hits={}
  for nm,h in allg.items():
   if nm==n:continue
   lb,ub=vec(h)
   if np.any(l>ub+5) or np.any(u<lb-5):continue
   gap=obj.min_gap(h,5)
   if gap<mg:mg,near0=gap,nm
   if gap<.00001:
    vol=(obj^h).volume()
    if vol>.0001:hits[nm]=round(vol,5)
  data[key]=dict(interferencia_mm3=hits,vecino=near0,margen_mm=round(mg,4))
 res[n]=data;print(n,data,flush=True)
(here/'Acceso_real_4_tornillos_P86.json').write_text(json.dumps(res,indent=1),'utf8')
