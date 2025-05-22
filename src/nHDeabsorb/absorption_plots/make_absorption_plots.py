"""
To run: [nHDeabsorb]$  python -m  absorption_plots.make_absorption_plots
"""

import pandas as pd
import get_absorption
import matplotlib.pyplot as plt
import numpy as np


# Set global plot parameters
plt.rcParams.update(
    {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
     'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 24,
     'legend.fontsize': 14})


def read_tcloutr_spec_data(fn):
    """Read dat file `fn` created by user in XSpec using tcloutr.

    The format of this file (order of the columns and so their meanings) is completely determined by the user.
    Check the XSpec commands that were issued to make sure this file is correctly read.

    An example of `fn` is `spec_default_bin.dat`.
    """
    # skip_rows ?
    dat = pd.read_csv(fn, header=0, delimiter=' ')
    # In keV
    energy = dat.iloc[:, 0].to_numpy()
    energy_half_bin_width = dat.iloc[:, 1].to_numpy()
    # This is an energy flux (in keV/cm^2/s) if `eeufspec` was used to write this file
    eflux = dat.iloc[:, 2].to_numpy()
    eflux_err = dat.iloc[:, 3].to_numpy()
    mdl_eflux = dat.iloc[:, 4].to_numpy()

    return energy, energy_half_bin_width, eflux, eflux_err, mdl_eflux


def plot_deabsorbed_spec(fn, fn_abs):
    """Plot observed spectrum and deabsorbed spectrum on the same axis"""
    energy, energy_half_bin_width, eflux, eflux_err, mdl_eflux = read_tcloutr_spec_data(fn)

    ebin_min = energy - energy_half_bin_width
    ebin_max = energy + energy_half_bin_width
    abs_bin_avg = get_absorption.xspec_absorption_component(ebin_min, ebin_max, fn_abs, nh=0.101)

    deabsorbed_eflux = eflux / abs_bin_avg

    plt.figure()
    plt.errorbar(energy, deabsorbed_eflux,
                 xerr=[energy - ebin_min, ebin_max - energy],
                 marker='s', markerfacecolor='none', ls=' ', label="Deabsorbed")
    plt.errorbar(energy, eflux,
                 xerr=[energy - ebin_min, ebin_max - energy],
                 marker='s', markerfacecolor='none', ls=' ', label="Observed")

    plt.xlabel('Energy [keV]')
    plt.loglog()
    plt.ylabel(r'Flux [keV/cm$^2$/s]')
    plt.legend()
    plt.savefig('example_spec.png')


def plot_both_absorption_tables(fn_abs_list, legend_labels):
    """Make a plot of the absorption components in `fn_abs_list`  and energy bin averages to check that the result is reasonable."""

    # Set global plot parameters
    plt.rcParams.update(
        {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
         'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 24,
         'legend.fontsize': 14})
    plt.figure()
    # Create some fake energy bins
    energy_interp = np.linspace(0.3, 1, 50)
    # energy_interp = np.logspace(-1, 1, 20)
    # # Truncate the plot to 0.3 to 10 keV
    # i = np.where((energy_interp > 0.3) & (energy_interp < 10))
    # energy_interp = energy_interp[i]
    ebin_min = energy_interp[:-1]
    ebin_max = energy_interp[1:]
    ebin_ctr = np.average((ebin_min, ebin_max), axis=0)

    for i, fn_abs in enumerate(fn_abs_list):
        # Can check `xspec_isolate_tbabs.sh` for header
        dat = pd.read_csv(fn_abs, header=0, delimiter='\s+')
        energy = dat['energy_kev'].to_numpy()
        # Truncate the plot
        idx = np.where((energy > 0.3) & (energy < 10))
        # This header name depends on the value of nH used (nH is here for record keeping),
        # so do not use the header name here
        absorb = dat.iloc[:, 1].to_numpy()[idx]
        energy = energy[idx]
        plt.scatter(energy, absorb, label=legend_labels[i], s=5, color='grey', alpha=0.5)

        '''
        plt.errorbar(ebin_ctr, xspec_absorb_component(ebin_min, ebin_max, fn_abs),
                     xerr=[ebin_ctr-ebin_min, ebin_max-ebin_ctr],
                    marker='s', label=f'Bin average {legend_labels[i]}', markerfacecolor='none', ls=' ')
        '''

    '''
    for num in [5, 10, 15, 20, 25, 35]:
        energy_interp = np.logspace(-0.52, 0, num)
        ebin_min = energy_interp[:-1]
        ebin_max = energy_interp[1:]
        ebin_ctr = np.average((ebin_min, ebin_max), axis=0)
        plt.errorbar(ebin_ctr, xspec_absorb_component(ebin_min, ebin_max, fn_abs),
                     xerr=[ebin_ctr-ebin_min, ebin_max-ebin_ctr], markerfacecolor='none', ls=' ', marker='|')
    '''

    for i in [1, 2, 3, 4, 5]:
        step_size = i*0.003
        ebin_ctr = np.arange(0.3, 0.6, step=step_size)
        ebin_min = ebin_ctr - step_size
        idx = np.where(ebin_min > 0.3)
        ebin_max = ebin_ctr + step_size
        ebin_min, ebin_max, ebin_ctr = ebin_min[idx], ebin_max[idx], ebin_ctr[idx]
        plt.errorbar(ebin_ctr, get_absorption.xspec_absorption_component(ebin_min, ebin_max, fn_abs),
                     xerr=[ebin_ctr-ebin_min, ebin_max-ebin_ctr], markerfacecolor='none', ls=' ', marker='|', label=f'step: {step_size} keV')

    plt.xlabel('Energy [keV]')
    plt.loglog()
    plt.ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
    plt.legend()
    plt.savefig('absorption_vs_energy.png')
    plt.xlim([0.3, 10])
    plt.savefig('absorption_vs_xrt_energy_range.png')


def plot_absorption_table(fn_abs, legend):
    # Set global plot parameters
    plt.rcParams.update(
        {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
         'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 24,
         'legend.fontsize': 14})
    plt.figure()
    dat = pd.read_csv(fn_abs, header=0, delimiter='\s+')
    energy = dat['energy_kev'].to_numpy()
    absorb = dat.iloc[:, 1].to_numpy()
    plt.scatter(energy, absorb, label=legend, s=5, color='grey', alpha=0.5)

    plt.xlabel('Energy [keV]')
    plt.loglog()
    plt.ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
    plt.legend()
    plt.title('100 eV - 100 keV')
    plt.savefig('absorption_plots/absorption_vs_energy.png')
    
    plt.figure()
    # Truncate the plot to XRT range
    idx = np.where((energy > 0.3) & (energy < 10))
    # This header name depends on the value of nH used (nH is here for record keeping),
    # so do not use the header name here
    plt.scatter(energy[idx], absorb[idx], label=legend, s=5, color='grey', alpha=0.5)
    plt.xlabel('Energy [keV]')
    plt.loglog()
    plt.ylabel(r'Absorption $e^{-\eta_H \sigma(E)}$')
    plt.legend()
    plt.title('Swift-XRT Energy Range')
    plt.savefig('absorption_plots/absorption_vs_xrt_energy_range.png')


if __name__ == "__main__":
    # Running from package directory nHDeabsorb/src/nHDeabsorb
    plot_absorption_table('absorption_tables/tbabs_abund_wilm_component.dat', 'TBabs')
