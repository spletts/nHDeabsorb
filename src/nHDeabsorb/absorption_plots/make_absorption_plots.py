"""
Plot absorption tables in make_table/
To run: [src/nHDeabsorb]$  python -m  absorption_plots.make_absorption_plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Set global plot parameters
plt.rcParams.update(
    {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
        'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 24,
        'legend.fontsize': 14})


def plot_absorption_table(fn_abs_list, legend_list):
    """Plot absorption values as a function of energy in `fn_abs_list`.
    The first element of `fn_abs_list` corresponds to the first element of `legend_list`.

    Parameters
    ----------
    fn_abs_list : list[str]
        List of filenames of the absorption tables produced by XSpec in make_table/
    legend_list : list[str]
        Labels for each filename in `fn_abs_list` in plot legend
    """
    
    markers = ['s', 'o']

    fig1, ax1 = plt.subplots(1, 1)
    fig2, ax2 = plt.subplots(1, 1)
    for i, fn_abs in enumerate(fn_abs_list):
        dat = pd.read_csv(fn_abs, header=0, delimiter='\s+')
        energy = dat['energy_kev'].to_numpy()
         # This header name depends on the value of nH used (nH is here for record keeping),
        # so do not use the header name here
        absorb = dat.iloc[:, 1].to_numpy()
        ax1.scatter(energy, absorb, label=legend_list[i], s=10, alpha=0.4, marker=markers[i])

        ax1.set_xlabel('Energy [keV]')
        ax1.loglog()
        ax1.set_ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
        ax1.legend()
        ax1.set_title('100 eV - 100 keV')
        fig1.savefig('absorption_plots/absorption_vs_energy.png')
    
        # Truncate the plot to XRT range
        idx = np.where((energy > 0.3) & (energy < 10))
        ax2.scatter(energy[idx], absorb[idx], label=legend_list[i], s=10, alpha=0.4, marker=markers[i])
        ax2.set_xlabel('Energy [keV]')
        ax2.loglog()
        ax2.set_ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
        ax2.legend()
        ax2.set_title('Swift-XRT Energy Range')
        fig2.savefig('absorption_plots/absorption_vs_xrt_energy_range.png')


if __name__ == "__main__":
    # Running from package directory nHDeabsorb/src/nHDeabsorb
    plot_absorption_table(['absorption_tables/tbabs_abund_wilm_component.dat', 'absorption_tables/phabs_component.dat'], ['TBabs', 'phabs'])
