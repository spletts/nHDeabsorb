"""
Get the photoionization absorption component given specific energy bins (in keV).
"""

import argparse
import logging
import pkg_resources
import sys
import os
import numpy as np


ABSORPTION_DICT = {'phabs': 'phabs_component.dat', 'tbabs_abund_wilm': 'tbabs_abund_wilm_component.dat'}
# Header for output file
HDR_OUT = 'energy_keV,ebin_width_keV,absorption'
LOG_FN = 'get_absorption.logging'


def interpolate_absorption(en, fn_abs):
    """Get the value of absorption at specific energy ``en`` (in keV) via interpolating a data table ``fn_abs`` which
    has the absorption component calculated by XSpec (see src/nHDeabsorb/make_table/).

    Parameters
    ----------
    en : array[float] or float
        Energy in keV
    fn_abs : str
        Filename for absorption table with implicit header: energy (in keV), corresponding absorption.
        Valid options:

        - src/nHDeabsorb/absorption_tables/phabs_component.dat
        - src/nHDeabsorb/absorption_tables/tbabs_abund_wilm_component.dat

        These were created in make_table/.
    Returns
    -------
    absorb : array_like[float] or float
        The (interpolated) absorption at energy ``en``
    """

    # Can check `xspec_isolate_tbabs.sh` for header
    dat = np.genfromtxt(fn_abs, skip_header=1)
    energy = dat[:, 0]
    mdl_flux = dat[:, 1]
    exp_factor_xspec = mdl_flux  # because norm=1 and idx=0; using tcloutr on plot model (not eemodel)

    absorb = np.interp(x=en, xp=energy, fp=exp_factor_xspec)

    return absorb


def xspec_absorption_component(ebin_min, ebin_max, absorption_model, nh=0.101):
    """Calculate the absorption value that XSpec uses in each energy bin, which is the average of the absorption
    at the bin edges. The absorption outside the energy range in the absorption table (``fn_abs``) is set to 1 (no absorption).

    Parameters
    ----------
    ebin_min : array_like[float] or float
        Lower bin edge(s) in keV
    ebin_max : array_like[float]  or float
        Upper bin edge(s) in keV
    absorption_model : str
        Which absorption model to use in the calculation.
        Valid options: 

        - tbabs_abdund_wilm
        - phabs

        The options correspond to the XSpec commands ``tbabs, abund wilm`` and ``phabs``, respectively.
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**.
        The default of nh=0.101 was used to create the tables in absorption_tables/.

    Returns
    -------
    abs_bin_avg : array_like[float] or float
        Absorption in the energy bin(s) [``ebin_min``, ``ebin_max``], as calculated by XSpec (averaged at bin edges)
    """

    fn_abs = pkg_resources.resource_filename('nHDeabsorb', os.path.join('absorption_tables', ABSORPTION_DICT[absorption_model]))

    # Get absorption at the bin edges, and take average of each bin
    abs_at_emin = interpolate_absorption(ebin_min, fn_abs)
    abs_at_emax = interpolate_absorption(ebin_max, fn_abs)
    abs_bin_avg = np.average((abs_at_emin, abs_at_emax), axis=0)

    # Check for energies outside the absorption range, and set absorption to 1 (no absorption)
    tbl_dat = np.genfromtxt(fn_abs, skip_header=1)
    tbl_energy = tbl_dat[:, 0]
    for i, _ in enumerate(abs_at_emin):
        if ebin_min[i] < min(tbl_energy) or ebin_max[i] > tbl_energy:
            abs_bin_avg[i] = 1
            logging.warning(f"Energy bin [{ebin_min[i]}, {ebin_max[i]}] keV lies outside the ranges in {fn_abs}, so the absorption is set equal to 1 (NO absorption).")

    # absorb2 = absorb1^(nH2/nH1); see README.md
    if nh != 0.101:
        abs_bin_avg = abs_bin_avg ** (nh / 0.101)

    return abs_bin_avg


def make_absorption_table(fn_sed_data, absorption_model, nh, fn_out):
    """Create a table of the absorption values corresponding to the energy bins in ``fn_sed_data``. 
    Save table as ``fn_out``.
    The absorption depends on ``absorption_model`` and ``nh``.

    Parameters
    ----------
    fn_sed_data : str
        Filename for SED data with:

        - No header. To change this behavior, edit ``skip_header``
        - Energy in keV in the first column. To change this requirement, edit ``energy = data[:, 0]`` with the relevant index
        - Energy bin width in keV in the second column.
        - Any remaining columns are not read.

        Note: User will need to rewrite the code to read their SED data unless it is formatted as above.
    absorption_model : str
        Which absorption model to calculate.
        Valid options:

        - tbabs_abdund_wilm
        - phabs.
        
        The options correspond to the XSpec commands ``tbabs, abund wilm`` and ``phabs``, respectively.
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**
    fn_out : str
        Filename for output data table which has explicit headers `HDR_OUT`: energy_keV,ebin_width_keV,absorption

    Returns
    -------
    abs_bin_avg : array_like[float] or float
        Absorption in the energy bin(s) [``ebin_min``, ``ebin_max``], as calculated by XSpec (averaged at bin edges)
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


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
    prog='get_absorption.py',
    description='Evaluate the photoionization absorption component given specific energy bins (in keV)',
    epilog='')
    logging.basicConfig(filename=LOG_FN, filemode='w', level=logging.DEBUG)
    make_absorption_table(fn_sed_data="sample_data/sed.dat", absorption_model="tbabs_abund_wilm", 
                           nh=0.157, fn_out="absorption.csv")
