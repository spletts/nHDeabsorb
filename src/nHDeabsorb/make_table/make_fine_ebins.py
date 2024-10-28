"""Make energy bin edges (in keV) and save to a file."""

import numpy as np
import pandas as pd


# Exponent for bin size (also for rounding)
expo = 3
bin_width = 2*10**-expo  # keV

# XSpec will calculate the middle i.e. the first bin is 0.3
emin, emax = 0.3-bin_width, 10+bin_width  # keV

# Round because:
# (Pdb) 9.7/0.01
# 969.9999999999999
num_bins = round((emax - emin)/bin_width)
ebins = np.round(np.linspace(emin, emax, num_bins), expo)
df = pd.DataFrame(data=ebins)
df.to_csv('ebin_edges.txt', index=False)
