from recolocar import *
import canal_bm_p45 as cad
rp=root/'V16_R1_G10_Ensayo_P45/Verificacion';old=cad.raw;new=readg(dest/'P45_BM_canal_sin_isla.npz');lost=readg(dest/'P45_BM_recorte_definitivo.npz')
def triangles(g):
 v,f=cad.verts(g);return v[f]
def split(tris,step):
 while True:
  edges=np.linalg.norm(tris-np.roll(tris,-1,axis=1),axis=-1).max(1)
  small=edges<=step
  if small.any():yield tris[small]
  big=tris[~small]
  if not len(big):break
  a,b,c=big.transpose(1,0,2);ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
  tris=np.concatenate([np.stack(x,axis=1) for x in ((a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca))])
def area(tris):return np.linalg.norm(np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),axis=1)/2
skin=-1000.
for t in split(triangles(lost),.18):
 d=sd(sskin,t.mean(1));skin=max(skin,max(d)+.18)
oldtree=tree(old);newtree=tree(new)
support={}
for n in ['P65','P83']:
 p=geom[n];area0=0.;area1=0.;area2=0.
 for t in split(triangles(p),.50):
  for cells in np.array_split(t,max(1,len(t)//65000)):
   ctr=cells.mean(1);a=area(cells);s0=abs(sd(oldtree,ctr))<.015;area0+=a[s0].sum()
   if s0.any():
    s1=abs(sd(newtree,ctr[s0]))<.015;area1+=a[s0][s1].sum()
 support[n]=dict(superficie_previa_de_contacto_muestreada_mm2=round(area0,3),superficie_conservada_muestreada_mm2=round(area1,3),porcentaje=round(area1*100/area0,4) if area0 else None)
l,u=vec(lost);hardware={}
for k,g in geom.items():
 a,b=vec(g)
 if k.startswith(('V15_HW','V8_','F_')) and np.all(l<b+4)&np.all(u>a-4):hardware[k]=round(lost.min_gap(g,4),4)
proof=dict(distancia_inferior_al_contorno_exterior_mm=round(float(-skin),4),metodo_exterior='Distancia firmada a envolvente exterior nominal sobre todas las caras del volumen retirado. Triángulos de lado máximo 0,18 mm y descuento adicional de 0,18 mm.',apoyos=support,metodo_apoyos='Área de los triángulos de la pieza vecina a menos de 0,015 mm de la superficie de P45, muestreo de lado máximo 0,50 mm. El área de contacto es aproximada.',distancias_a_herrajes_mm=hardware)
print(proof,flush=True);save(rp/'Superficie_exterior_y_apoyos_de_P45.json',proof)
