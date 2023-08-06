#!/usr/bin/env python3
import timeit

import numpy as np

from extraction.core.functions.custom.localisation import nuc_est_conv

image_size = 100
mask_size = 20
image = np.reshape(
    np.random.randint(100, size=image_size**2), (image_size, image_size)
)
mask = np.pad(
    np.ones((mask_size, mask_size)), (image_size - mask_size) // 2
).astype(bool)

wrapped = nuc_est_conv(mask, image)
# timeit.timeit(wrapped, number=1000)
# import cProfile
# import pstats

# profile = cProfile.Profile()
# profile.runcall(wrapped)
# ps = pstats.Stats(profile)
# ps.print_stats()
