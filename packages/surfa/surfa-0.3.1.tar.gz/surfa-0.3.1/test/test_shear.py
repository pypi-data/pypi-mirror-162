import surfa as sf
import numpy as np


orig = sf.load_volume('test/orig.mgz')
aff = sf.transform.affine.compose_affine([4, 2, 1], [25, 23, 13], shear=(0.1, 0.2, 0.1))
orig = orig.transform(aff, resample=False)

print(orig.geom.rotation)
print(orig.geom.shear)
