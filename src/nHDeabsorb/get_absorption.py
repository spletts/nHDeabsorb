"""
Get the photoionization absorption component given specific energy bins (in keV) and save to a table.

The filename of the table created is written to log file get_absorption.logging
"""

import argparse
import logging
import pkg_resources
import sys

import numpy as np

PARSER = argparse.ArgumentParser(
    prog='get_absorption.py',
    description='Evaluate the photoionization absorption component given specific energy bins (in keV)',
    epilog='')
ABSORPTION_DICT = {'phabs': 'phabs_component.dat', 'tbabs_abund_wilm': 'tbabs_abund_wilm_component.dat'}
# Energy ranges (keV) which are affected by absorption
MIN_ABSORPTION_ENERGY = 0.3
MAX_ABSORPTION_ENERGY = 10.0
HDR_OUT = 'energy_keV,ebin_width_keV,absorption'
LOG_FN = 'get_absorption.logging'
logging.basicConfig(filename=LOG_FN, filemode='w', level=logging.DEBUG)


def interpolate_absorption(en, fn_abs):
    """Get the value of absorption component at specific energy `en` (in keV) via interpolating a data table `fn` which
    has the absorption component calculated by XSpec (see make_table/xspec_isolate_phabs.sh for an example).

    Parameters
    ----------
    en : array[float] or float
        Energy in keV
    fn_abs : str
        File with implicit headers: energy (in keV), corresponding absorption component values
        Valid options - phabs_component.dat, tbabs_abund_wilm_component.dat

    Returns
    -------
    array_like[float] or float
    The interpolated absorption component at energy `en`
    """

    # Can check `xspec_isolate_tbabs.sh` for header
    # dat = read_csv(fn, header=0, delimiter='\s+')
    # energy = dat['energy_kev'].to_numpy()
    # mdl_flux = dat.iloc[:, 1].to_numpy()
    dat = np.genfromtxt(fn_abs, skip_header=1)
    energy = dat[:, 0]
    mdl_flux = dat[:, 1]
    # This header name depends on the value of nH used (nH is in the header for record keeping),
    # so do not use the header name here
    exp_factor_xspec = mdl_flux  # because norm=1 and idx=0; using tcloutr on plot model (not eemodel)

    y = np.interp(x=en, xp=energy, fp=exp_factor_xspec)

    return y


def xspec_absorption_component(ebin_min, ebin_max, absorption_model, nh=0.101):
    """Calculate the absorption value that XSpec uses in each energy bin, which is the average of the absorption
    at the bin edges.

    The absorption outside 0.3-10 keV is set to 1 (no absorption).

    'Tbabs evaluates the cross-section at each end of the energy bin and averages them.'
    -Kieth via xspec12@athena.gsfc.nasa.gov
    NOTE: unknown analytic formula for the cross section which XSpec uses for TBabs + abund_wilm and phabs

    Parameters
    ----------
    ebin_min : array_like[float] or float
        Lower bin edges in keV
    ebin_max : array_like[float]  or float
        Upper bin edges in keV
    absorption_model : str
        Which absorption model to calculate.
        Valid options - tbabs_abdund_wilm, phabs
        which correspond to the XSpec commmands >tbabs >abund wilm and >phabs
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**
        The default 0.101 was used to create the tables phabs_component.dat and tbabs_abund_wilm_component.dat

    Returns
    -------
    array_like[float] or float
    """

    fn_abs = pkg_resources.resource_filename(__name__, ABSORPTION_DICT[absorption_model])

    # idx_no_absorb = np.where((ebin_min < 0.3) | (ebin_max > 10))

    # Get absorption at the bin edges, and take average of each bin
    abs_at_emin = interpolate_absorption(ebin_min, fn_abs)
    abs_at_emax = interpolate_absorption(ebin_max, fn_abs)
    abs_bin_avg = np.average((abs_at_emin, abs_at_emax), axis=0)

    # Check for energies outside the absorption range, and set absorption to 1 (no absorption)
    for i, _ in enumerate(abs_at_emin):
        if ebin_min[i] < MIN_ABSORPTION_ENERGY or ebin_max[i] > MAX_ABSORPTION_ENERGY:
            abs_bin_avg[i] = 1

    # absorb2 = absorb1^(nH2/nH1); see README.md
    if nh != 0.101:
        abs_bin_avg = abs_bin_avg ** (nh / 0.101)

    return abs_bin_avg


def make_absorption_table(fn_sed_data, absorption_model, nh, fn_out):
    """Create a table of the absorption corresponding to the energy bins in `fn_sed_data`.
    The absorption component is set by `absorption_model` and `nh`.
    If `absorption_model` is not recognized the program will exit.

    Parameters
    ----------
    fn_sed_data : str
        Filename for SED data which must have:
        - No header
            To change this behavior, edit `skip_header`
        - Energy in keV in the first column
            To change this requirement, edit `energy = data[:, 0]` with the relevant index
        - Energy bin width in keV in the second column.
        The remaining columns are not read.
    absorption_model : str
        Which absorption model to calculate.
        Valid options - tbabs_abdund_wilm, phabs
        which correspond to the XSpec commmands >tbabs >abund wilm and >phabs
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**
    fn_out : str
        Filename for output data table which has explicit headers `HDR_OUT` - energy_keV,ebin_width_keV,absorption
    """
    data = np.genfromtxt(fn_sed_data, skip_header=0)
    energy = data[:, 0]
    ebin_width = data[:, 1]
    ebin_min, ebin_max = energy - ebin_width, energy + ebin_width
    if absorption_model not in ABSORPTION_DICT.keys():
        err_msg = f'{absorption_model} not a valid absorption model; must be one of: {ABSORPTION_DICT.keys()}'
        logging.info(err_msg)
        sys.exit(err_msg)
    else:
        abs_bin_avg = xspec_absorption_component(ebin_min, ebin_max, absorption_model, nh)
        np.savetxt(fn_out, np.c_[energy, ebin_width, abs_bin_avg], delimiter=',', comments='',
                   header='energy_keV,ebin_width_keV,absorption')
        logging.info(f'Wrote {fn_out}')

    return abs_bin_avg 

