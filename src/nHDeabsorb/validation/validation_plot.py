"""
Plot XSpec's evaluated of the total model and 
powerlaw*absoprtion where 'absorption' is evaluated by nHDeabsorb and 'powerlaw' (or other intrinsic model) is evaluated using the best fit parameters.
These should be identical.

To run: [src/nHDeabsorb]$  python -m  validation.validation_plot
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import logging
import sys

import get_absorption
import os

# Set global plot parameters
plt.rcParams.update(
    {'font.size': 16, 'figure.figsize': (10, 8), 'axes.grid.which': 'both',
        'grid.color': 'gainsboro', 'grid.linestyle': 'dotted', 'axes.grid': True, 'axes.labelsize': 16,
        'legend.fontsize': 12})


def powlaw_params(fn_param):
    tbl = pd.read_csv(fn_param, header=0, delimiter=' ')
    #  PhoIndex, norm
    idx, norm = tbl.iloc[:, 1][:2]

    return idx, norm


def plot_seds(fn_sed_data, fn_param, absorption_model, nh, obsid, fn_plot="sed.png", is_eflux=True, intrinsic_model="powlaw"):

    color_avg_over_bin = "tab:blue"
    color_endpoint_avg = "tab:orange"

    # SED data
    sed_data = np.genfromtxt(fn_sed_data, skip_header=0)
    sed_energy = sed_data[:, 0]
    ebin_width = sed_data[:, 1]
    ebin_min, ebin_max = sed_energy - ebin_width, sed_energy + ebin_width
    # Energy or photon flux from model; no error is given with this value
    sed_model_flux = sed_data[:, 4]

    # Best fit intrinsic parameters
    if intrinsic_model == "powlaw":
        idx, norm = powlaw_params(fn_param)
    else:
        sys.exit(f"Model {model} not recognized. Edit this script to implement")

    # Set up axes
    fig = plt.figure(figsize=(14, 12))
    gs = fig.add_gridspec(3, hspace=0)
    axs = gs.subplots(sharex=True)

    # Upper plot
    axs[0].errorbar(sed_energy, sed_model_flux, xerr=ebin_width, markerfacecolor="none", color="k", label="XSpec model", marker='s', ls=' ')

    if is_eflux:
        # Flux from best fit parameters to intrinsic SED
        intrinsic_bestfit_flux = norm * np.power(sed_energy, -idx+2)
        axs[0].set_ylabel('Observed energy flux\n' + rf'[keV/cm$^2$/s]')
        axs[2].set_ylabel('Residual flux\n' + rf'[keV/cm$^2$/s]')
    else: 
        intrinsic_bestfit_flux = norm * np.power(sed_energy, -idx)
        axs[0].set_ylabel('Observed photon flux\n' + rf'[ph/cm$^2$/s]')
        axs[2].set_ylabel('Residual flux\n' + rf'[ph/cm$^2$/s]')

    colors = [color_endpoint_avg, color_avg_over_bin]
    plot_labels = ["(at endpoints)", "(over bins)"]
    for i, calc_avg_using_endpoints in enumerate([True, False]):
        # Absorption with different methods depending on `calc_avg_using_endpoints`
        abs_avg = get_absorption.xspec_absorption_component(ebin_min, ebin_max, absorption_model, calc_avg_using_endpoints, nh)
        axs[0].errorbar(sed_energy,  intrinsic_bestfit_flux * abs_avg, xerr=ebin_width, label=f"nHDeabsorb {plot_labels[i]}", marker=".", ls=' ', color=colors[i])
        # Express residuals as percentages
        resid_percent = 100*((intrinsic_bestfit_flux * abs_avg) - sed_model_flux)/sed_model_flux
        axs[1].scatter(sed_energy, resid_percent, color=colors[i], marker='.', label=rf"100%[nHDeabsorb {plot_labels[i]} $-$ XSpecModel]/XSpecModel")
        # Flux residual
        resid_flux = (intrinsic_bestfit_flux * abs_avg) - sed_model_flux
        axs[2].scatter(sed_energy, resid_flux, color=colors[i], marker='x', label=rf"nHDeabsorb {plot_labels[i]} $-$ XSpecModel")

    p = 0.5
    axs[1].axhspan(-p, p, color="grey", alpha=0.1, label=rf"$\pm${p}%")   
    for ax in [axs[1], axs[2]]:
        ax.axhline(0, color='grey', ls='--')
        # These vertical axes can have negative values, no log scale
        ax.set_xscale('log')
    axs[1].set_ylabel('Residual %')
    axs[2].set_xlabel('Energy [keV]')
    axs[0].loglog()
    for ax in axs:
        ax.legend()
    # plt.tight_layout()
    plt.suptitle(f"Observed (not intrinsic) SED for ObsID: {obsid}")
    plt.savefig(fn_plot)


if __name__ == "__main__":
    logging.basicConfig(filename='validation/_validation_plot.log', filemode='w', level=logging.INFO)
   
    model = "powlaw_tbabs"
    for obsid in ["00032646001", "00032646035", "00041535055"]:
        # relative to src/nHDeabsorb
        result_dir = os.path.join("validation/xspec_ana", obsid, model)
        plot_seds(fn_sed_data=os.path.join(result_dir, "spec_default_bin.dat"), 
              fn_param=os.path.join(result_dir, "param_tbl.dat"), 
              absorption_model="tbabs_abund_wilm", 
              nh=0.157,
              is_eflux=True,
              # relative to src/nHDeabsorb
              fn_plot=f"validation/sed_eflux_{obsid}.png",
              obsid=obsid)

    
    # Photon flux. ObsID 00032646010 was used to make the tables in nHDeabsorb, but it shouldn't matter
    plot_seds(fn_sed_data="validation/xspec_ana/00032646010/powlaw_tbabs/spec_default_bin_ufspec.dat", 
              fn_param="validation/xspec_ana/00032646010/powlaw_tbabs/param_tbl.dat", 
              absorption_model="tbabs_abund_wilm", 
              nh=0.157,
              is_eflux=False,
              fn_plot=f"validation/sed_phflux_00032646010.png",
              obsid='00032646010')
    
    # Energy flux
    plot_seds(fn_sed_data="validation/xspec_ana/00032646010/powlaw_tbabs/spec_default_bin_eeufspec.dat", 
              fn_param="validation/xspec_ana/00032646010/powlaw_tbabs/param_tbl.dat", 
              absorption_model="tbabs_abund_wilm", 
              nh=0.157,
              is_eflux=True,
              fn_plot=f"validation/sed_eflux_00032646010.png",
              obsid='00032646010')
    