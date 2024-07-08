"""
Get the absorption component in each energy bin.

Use the table 'tbabs_component.dat' to interpolate/evaluate the absorption component at the bin edges. Then take the average. This is the value XSpec uses.
'Tbabs evaluates the cross-section at each end of the energy bin and averages them.' -Kieth via xspec12@athena.gsfc.nasa.gov
"""

import matplotlib.pyplot as plt
from numpy import interp
from pandas import read_csv
import numpy as np


def interpolate_absorption(en, fn):
    """Get the value of absorption component at specific energy `en` (in keV) via interpolating a data table `fn` that
    has the absorption component determined from XSpec.

    Parameters
    ----------
    en : float or array[float]
        Energy (keV)
    fn : str
        File with headers: energy (in keV), corresponding absorption component values

    Returns
    -------
    array_like[float] or float
    The interpolated absorption component at energy `en`
    """

    # Can check `xspec_isolate_tbabs.sh` for header
    dat = read_csv(fn, header=0, delimiter='\s+')
    energy = dat['energy_kev'].to_numpy()
    # This header name depends on the value of nH used (nH is in the header for record keeping),
    # so do not use the header name here
    mdl_flux = dat.iloc[:, 1].to_numpy()
    exp_factor_xspec = mdl_flux  # because norm=1 and idx=0; using wd on plot model (not eemodel)

    y = interp(x=en, xp=energy, fp=exp_factor_xspec)

    return y


def xspec_absorb_component(ebin_min, ebin_max, fn_abs, nh=0.101):
    """Calculate the absorption value that XSpec uses, which is the average of the absorption at the bin edges.

    'Tbabs evaluates the cross-section at each end of the energy bin and averages them.' -Kieth via xspec12@athena.gsfc.nasa.gov
    NOTE: Due to no known analytic formula for whatever equation XSpec uses for TBabs,
    I have to evaluate the absorption at the bin edges via *interpolation*.

    Parameters
    ----------
    ebin_min : array_like[float]
        Lower bin edges in keV
    ebin_max : array_like[float]
        Upper bin edges in keV
    fn_abs : str
        File with headers: energy (in keV), corresponding absorption component values
        Ex - phabs_component.dat
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**

    Returns
    -------
    array_like[float]
    """

    # Get absorption at the bin edges, and take average of each bin
    abs_at_emin = interpolate_absorption(ebin_min, fn_abs)
    abs_at_emax = interpolate_absorption(ebin_max, fn_abs)
    abs_bin_avg = np.average((abs_at_emin, abs_at_emax), axis=0)

    if nh != 0.101:
        abs_bin_avg = abs_bin_avg**(nh/0.101)

    return abs_bin_avg


def plot_absorption(fn_abs_list, legend_labels, color_list=['tab:blue', 'tab:orange', 'tab:green']):
    """Make a plot of the absorption components in `fn_abs_list`  and energy bin averages to check that the result is reasonable."""

    # Set global plot parameters
    plt.rcParams.update(
        {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
         'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 24,
         'legend.fontsize': 14})

    # Create some fake energy bins
    energy_interp = np.linspace(0.3, 10, 10**2)
    # energy_interp = np.logspace(-1, 1, 20)
    # # Truncate the plot to 0.3 to 10 keV
    # i = np.where((energy_interp > 0.3) & (energy_interp < 10))
    # energy_interp = energy_interp[i]
    ebin_min = energy_interp[:-1]
    ebin_max = energy_interp[1:]
    ebin_ctr = np.average((ebin_min, ebin_max), axis=0)

    for i, fn_abs in enumerate(fn_abs_list):
        # Can check `xspec_isolate_tbabs.sh` for header
        dat = read_csv(fn_abs, header=0, delimiter='\s+')
        energy = dat['energy_kev'].to_numpy()
        # Truncate the plot to 0.3 to 10 keV
        idx = np.where((energy > 0.3) & (energy < 10))
        # This header name depends on the value of nH used (nH is here for record keeping),
        # so do not use the header name here
        absorb = dat.iloc[:, 1].to_numpy()[idx]
        energy = energy[idx]
        plt.scatter(energy, absorb, label=legend_labels[i], s=5, color=color_list[i], alpha=0.5)

        plt.errorbar(ebin_ctr, xspec_absorb_component(ebin_min, ebin_max, fn_abs),
                     xerr=[ebin_ctr-ebin_min, ebin_max-ebin_ctr],
                    marker='s', label=f'Bin average {legend_labels[i]}', markerfacecolor='none', ls=' ')

    plt.xlabel('Energy [keV]')
    plt.loglog()
    plt.ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
    plt.legend()
    plt.savefig('plot_of_absorption.png')


if __name__ == "__main__":
    plot_absorption(["tbabs_component.dat", "phabs_component.dat"], ['tbabs & abund wilm', 'phabs'])
