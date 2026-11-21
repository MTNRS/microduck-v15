from pathlib import Path
here=Path(__file__).parent
exec(compile((here/'cierre_con_solidos.py').read_text('utf-8-sig').split('for n in sys.argv[1:]')[0],str(here/'cierre_con_solidos.py'),'exec'))
out=[]
for n in range(1,4):
 sw=readg(here/f'P86_tramo_{n}.npz');low,high=vec(sw);d0={};penetrations={};nearby=0
 for k,h in allg.items():
  l,u=vec(h)
  if np.any(l>high+1.5) or np.any(u<low-1.5):continue
  nearby+=1;mg=sw.min_gap(h,1.5)
  if mg<1.4999:
   d0[k]=round(float(mg),5)
   if mg<.0001:
    vol=(sw^h).volume()
    if abs(vol)>1.e-6:penetrations[k]=round(vol,7)
 out.append(dict(tramo=n,solidos_comprobados=len(allg),candidatos_tras_caja=nearby,proximidades_inferiores_a_1p5_mm=d0,intersecciones_superiores_a_1e_6_mm3=penetrations));print('VER',n,d0,penetrations,flush=True)
(here/'P86_782_solidos_barridos_exactos.json').write_text(json.dumps(out,indent=1),'utf8')
