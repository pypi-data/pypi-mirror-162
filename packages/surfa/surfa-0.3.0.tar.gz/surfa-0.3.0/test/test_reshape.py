import surfa as sf
import numpy as np


orig = sf.load_volume('test/orig.mgz')
mf = orig.new(np.stack((orig.data, orig.data + np.random.normal(size=orig.shape) * 40), axis=-1))

kwargs = dict(shape=(80, 80, 80), voxsize=1, orientation='RAS', dtype='float32', copy=False)
mfc = mf.conform(**kwargs)
sfc = orig.conform(**kwargs)

sf.vis.fv(orig, mfc, sfc)
