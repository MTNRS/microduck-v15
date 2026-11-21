from pathlib import Path
import sys,tempfile,os
T=Path(tempfile.gettempdir());sys.path[:0]=[str(T/'md17audbm'),str(T)]
os.environ['MD16_CHECK']='Tendido_15_montaje_G8b'
code=(T/'md17audbm/electronics.py').read_text('utf-8-sig')
exec(compile(code[:code.index('for c in con:')],str(T/'md17audbm/electronics.py'),'exec'))
here=Path(__file__).parent
for c in con:
 center=np.array(c['center']);half=np.array(c['size'])/2
 allg[c['id']]=union(*[readg(f) for f in W.glob('G4_XT30_*.npz')]) if c['id'].startswith('XT30') else box(center-half,center+half)
exclude=[k for k in allg if k=='P86' or k.startswith(('barrido_','F_M2x6_'))]
for k in exclude:del allg[k]
g=readg(here/'P86_alivio_interior.npz');lower,upper=vec(g);counts={}
def sweep(path):
 record=[];cap=1.1;flags={}
 for a,b in zip(np.array(path,float),np.array(path[1:],float)):
  delta=b-a;span=np.linalg.norm(delta);axis=delta/span;results={}
  L=lower+np.minimum(a,b);H=upper+np.maximum(a,b)
  for k,h in allg.items():
   lo,hi=vec(h)
   if np.any(lo>H+cap) or np.any(hi<L-cap):continue
   counts[k]=counts.get(k,0)+1;worst=cap;impact=None;calls=0
   def visit(t,semi):
    nonlocal worst,impact,calls
    if impact is not None:return
    pose=a+axis*t
    gapbox=np.linalg.norm(np.maximum(np.maximum(lo-(upper+pose),(lower+pose)-hi),0))
    if gapbox-semi>=worst:return
    piece=g.translate(pose.tolist());d=piece.min_gap(h,semi+cap+.01);calls+=1
    if d==0:
     vol=(piece^h).volume()
     if vol>1.e-5:impact=[round(vol,6),pose.round(5).tolist()];return
    low=d-semi
    if low>=worst:return
    if semi<.016 or low>=.65:
     worst=min(worst,low);return
    visit(t-semi/2,semi/2);visit(t+semi/2,semi/2)
   for i in np.arange(0,span,4.): 
    u=min(i+4,span);visit((i+u)/2,(u-i)/2)
   if worst<cap or impact:
    results[k]=dict(margen_inferior_mm=round(worst,4) if not impact else None,interseccion=impact,evaluaciones=calls)
    if impact or worst<.12:print('min',k,results[k],flush=True)
  record.append(dict(desde=a.tolist(),hasta=b.tolist(),proximidades=results));print('tramo listo',a,b,len(results),flush=True)
 return dict(total_solidos=len(allg),envolventes_de_empalmes_y_conectores=len(con),excluidos=exclude,tramos=record,metodo='Distancia entre mallas con poda por cajas y por distancia de Hausdorff de cada traslación. Se resta el semidesplazamiento del intervalo; intersección de volumen calculada si la distancia es cero. Las cuatro fijaciones de la propia tapa se ponen después.')
paths={'oblicua':[[-90,0,14],[-18,0,14],[0,0,8],[0,0,0]],'escalon':[[-90,0,14],[-12,0,14],[-12,0,8],[0,0,8],[0,0,0]]}
paths.update({f'entrada_{h}':[[-90,0,14],[-18,0,14],[0,0,h],[0,0,0]] for h in (9,10,11)})
for n in sys.argv[1:]:
 x=sweep(paths[n]);(here/('P86_cierre_solidos_'+n+'.json')).write_text(json.dumps(x,indent=1),'utf8')
