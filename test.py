import time

tmp = time.time()

time.sleep(0.1)

tmp = time.time() - tmp

import numpy as np
print(tmp)
print(np.float32(tmp))
