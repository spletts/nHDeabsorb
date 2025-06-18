"""
Get the photoionization absorption component given specific energy bins (in keV).
"""

import argparse
import logging
import pkg_resources
import sys
import os
import numpy as np
from scipy import interpolate


ABSORPTION_DICT = {'phabs': 'phabs_component.dat', 'tbabs_abund_wilm': 'tbabs_abund_wilm_component.dat'}
# Header for output file
HDR_OUT = 'energy_keV,ebin_width_keV,absorption'
LOG_FN = '_get_absorption.logging'


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

    # Parameters are x and y of data
    absorb_function = interpolate.interp1d(x=energy, y=exp_factor_xspec, kind='cubic')
    absorb = absorb_function(en)

    return absorb


def average_absorption_per_bin(ebin_min, ebin_max, absorption_model, nh=0.101):
    """Calculate the absorption value by averaging the absorption in each energy bin using all points in the table ``fn_abs`` which fall in the bin. 
    The absorption outside the energy range in the absorption table (``fn_abs``) is set to 1 (no absorption).

    Parameters
    ----------
    ebin_min : array_like[float]
        Lower bin edge(s) in keV
    ebin_max : array_like[float]
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
    abs_avg_over_bin : array_like[float]
        Absorption in the energy bin(s) [``ebin_min``, ``ebin_max``], as calculated averaging the absorption at all points within the energy range in the table ``fn_abs``
    """

    try:
        fn_abs = pkg_resources.resource_filename('nHDeabsorb', os.path.join('absorption_tables', ABSORPTION_DICT[absorption_model]))
    except OSError:  # file not found
        logging.warning(f"File {fn_abs} not found with pkg_resources")
        print(f"File {fn_abs} not found with pkg_resources")
        fn_abs = os.path.join('absorption_tables', ABSORPTION_DICT[absorption_model])
        logging.info(f"Looking for {fn_abs}")

    logging.info(f'Averaging table {fn_abs}')

    dat = np.genfromtxt(fn_abs, skip_header=1)
    tbl_energy = dat[:, 0]

    abs_avg_over_bin = []

    # Average in each bin
    for i, emin in enumerate(ebin_min):
        emax = ebin_max[i]
        # Ensure energy is covered by the table
        if emin < min(tbl_energy) or emax > max(tbl_energy):
            abs_avg_over_bin.append(1)
            logging.warning(f"Energy bin [{ebin_min[i]}, {ebin_max[i]}] keV lies outside the ranges in {fn_abs}, so the absorption is set equal to 1 (NO absorption).")
        else:
            dat_mask = dat[(dat[:, 0] > emin) & (dat[:, 0] <= emax)]
            absorb_mask = dat_mask[:, 1]
            abs_avg_over_bin.append(np.average(absorb_mask))

    # absorb2 = absorb1^(nH2/nH1)
    if nh != 0.101:
        abs_avg_over_bin = np.array(abs_avg_over_bin) ** (nh / 0.101)

    return abs_avg_over_bin


def xspec_absorption_component(ebin_min, ebin_max, absorption_model, calc_avg_using_endpoints=False, nh=0.101):
    """Calculate the absorption value in each energy bin. Calculated according to ``calc_avg_using_endpoints`` (see docstring)).
    The absorption outside the energy range in the absorption table (``fn_abs``) is set to 1 (no absorption).

    Parameters
    ----------
    ebin_min : array_like[float]
        Lower bin edge(s) in keV
    ebin_max : array_like[float]
        Upper bin edge(s) in keV
    absorption_model : str
        Which absorption model to use in the calculation.
        Valid options: 

        - tbabs_abdund_wilm
        - phabs

        The options correspond to the XSpec commands ``tbabs, abund wilm`` and ``phabs``, respectively.
    calc_avg_using_endpoints : bool
        If True, calculates the absorption in each bin by averaging the absorption at the endpoints of each bin.
        The absorption at the specific endpoint energy is evaluated by interpolating a table ``fn_abs``. This is how XSpec calculates it.
        If False, calculates the absorption in each bin by averaging all the absorption values that lie within each bin. There is no interpolation in this case.
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**.
        The default of nh=0.101 was used to create the tables in absorption_tables/.

    Returns
    -------
    abs_bin_avg : array_like[float]
        Absorption in the energy bin(s) [``ebin_min``, ``ebin_max``].
    """
    # TODO handle this more effectively?
    try:
        fn_abs = pkg_resources.resource_filename('nHDeabsorb', os.path.join('absorption_tables', ABSORPTION_DICT[absorption_model]))
    except OSError:  # file not found
        logging.warning(f"File {fn_abs} not found with pkg_resources")
        print(f"File {fn_abs} not found with pkg_resources")
        fn_abs = os.path.join('absorption_tables', ABSORPTION_DICT[absorption_model])
        logging.info(f"Looking for {fn_abs}")

    logging.info(f'Interpolating table {fn_abs}')

    dat = np.genfromtxt(fn_abs, skip_header=1)
    tbl_energy = dat[:, 0]

    if calc_avg_using_endpoints:
        # Get absorption at the bin edges, and take average of each bin
        abs_at_emin = interpolate_absorption(ebin_min, fn_abs)
        abs_at_emax = interpolate_absorption(ebin_max, fn_abs)
        abs_in_bins = np.average((abs_at_emin, abs_at_emax), axis=0)
        # Check for energies outside the absorption range, and set absorption to 1 (no absorption). The interpolation will still return a value
        for i, _ in enumerate(abs_at_emin):
            if ebin_min[i] < min(tbl_energy) or ebin_max[i] > max(tbl_energy):
                abs_in_bins[i] = 1
                logging.warning(f"Energy bin [{ebin_min[i]}, {ebin_max[i]}] keV lies outside the ranges in {fn_abs}, so the absorption is set equal to 1 (NO absorption).")
    else:
        abs_in_bins = []
        # Average in each bin
        for i, emin in enumerate(ebin_min):
            emax = ebin_max[i]
            # Ensure energy is covered by the table
            if emin < min(tbl_energy) or emax > max(tbl_energy):
                abs_in_bins.append(1)
                logging.warning(f"Energy bin [{ebin_min[i]}, {ebin_max[i]}] keV lies outside the ranges in {fn_abs}, so the absorption is set equal to 1 (NO absorption).")
            else:
                dat_mask = dat[(dat[:, 0] > emin) & (dat[:, 0] <= emax)]
                absorb_mask = dat_mask[:, 1]
                abs_in_bins.append(np.average(absorb_mask))
        abs_in_bins = np.array(abs_in_bins)

    # absorb2 = absorb1^(nH2/nH1)
    if nh != 0.101:
        abs_in_bins = abs_in_bins ** (nh / 0.101)

    return abs_in_bins


def make_absorption_table(fn_sed_data, absorption_model, nh, fn_out, calc_avg_using_endpoints=False):
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
    calc_avg_using_endpoints : bool
        If True, calculates the absorption in each bin by averaging the absorption at the endpoints of each bin.
        The absorption at the specific endpoint energy is evaluated by interpolating a table ``fn_abs``. This is how XSpec calculates it.
        If False, calculates the absorption in each bin by averaging all the absorption values that lie within each bin. There is no interpolation in this case.
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
        abs_bin_avg = xspec_absorption_component(ebin_min, ebin_max, absorption_model, calc_avg_using_endpoints, nh)
        np.savetxt(fn_out, np.c_[energy, ebin_width, abs_bin_avg], delimiter=',', comments='',
                   header='energy_keV,ebin_width_keV,absorption')
        logging.info(f'Wrote {fn_out}')

    return abs_bin_avg


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
                prog='get_absorption.py',
                description='Evaluate the photoionization absorption component given specific energy bins (in keV)',
                epilog='')
    logging.basicConfig(filename=LOG_FN, filemode='w', level=logging.INFO)
    make_absorption_table(fn_sed_data="sample_data/sed.dat", absorption_model="tbabs_abund_wilm", 
                           nh=0.157, fn_out="absorption.csv",
                           calc_avg_using_endpoints=False)
