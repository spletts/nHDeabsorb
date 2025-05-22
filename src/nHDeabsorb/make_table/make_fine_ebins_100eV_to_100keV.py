"""Make energy bin edges (in keV) and save to a file."""

import numpy as np
import pandas as pd


# XSpec will calculate the middle 
emin, emax = 0.1, 100  # keV

num_bins = 10**3 
# In my experience typical SEDs bins change on order of 0.02 keV, so rounding to ~0.0001 keV for interpolation should be sufficient
ebins = np.round(np.logspace(np.log10(emin), np.log10(emax), num_bins), 4)
df = pd.DataFrame(data=ebins)
df.to_csv('ebin_edges_100eV_to_100keV.txt', index=False, header=None)

