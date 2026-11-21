from prisma import *
import sys
# The lid is rigid and its orientation is constant across these three translations.
keyframes=np.array([[-90.,0,14.],[-18.,0,14.],[0,0,10.],[0,0,0.]])
gg=geom(here/'P86_alivio_interior.npz');shapes=[]
for i,(a,b) in enumerate(zip(keyframes,keyframes[1:])):
 sw=sweep_exact(gg,b-a).translate(a);saveg('P86_tramo_'+str(i+1),sw);shapes.append(sw)
saveg('barrido_entrada_G9',union(shapes[:2]));saveg('barrido_bajada_G9',shapes[2])
