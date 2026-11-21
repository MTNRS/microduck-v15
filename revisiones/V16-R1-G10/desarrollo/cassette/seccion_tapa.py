from pathlib import Path
import numpy as np,sys,tempfile
T=Path(tempfile.gettempdir());sys.path[:0]=[str(T/'md8lib'),str(T/'md7lib'),str(T)];import manifold3d as m
v=np.load(T/'md8work/P86.npz');g=m.Manifold(m.Mesh64(v['v'],v['f'].astype('uint64')));r=[]
for x,y in ((-3.0,-3.5),(-3,.3),(-3.39,.36),(-2.5,-4),(-4.1,-7),(2.72,1.8),(-5.,-1.27)):
 hits=g.ray_cast([x,y,145],[x,y,181]);print((x,y),[np.round(h.position[2],4) for h in hits])
