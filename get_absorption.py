"""
Get the photoionization absorption component given specific energy bins (in keV) and save to a table.

Command line parameters are written to log file get_absorption.logging
The filename of the table created is written to log file get_absorption.logging
"""

import argparse
import logging
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
PARSER.add_argument('absorption_model', type=str, help=f'Valid options are: {ABSORPTION_DICT.keys()}.')
PARSER.add_argument('nH', type=float, help='Hydrogen column density in units of 10^22 1/cm^2.')
PARSER.add_argument('fn_energy_data', type=str,
                    help='Filename of data file which contains the energy bin centers (in keV) in the first column '
                         'and the energy bin width (in keV) in the second column. This file must not have a header '
                         '(to change this behavior see the docstring for `make_absorption_table`). This file can have any number of columns, '
                         'as only the first two are read.')
PARSER.add_argument('--fn_output', type=str, default='absorption.csv',
                    help=f'Filename of output data file which contains the energy bin centers (in keV) in the first '
                         f'column, and the energy bin width (in keV) in the second column, and the corresponding '
                         f'absorption component in the third a nd final column. Energies outside the range 0.3-10 keV '
                         f'have absorption=1 (corresponding to no absorption).'
                         f'This comma-separated file has header {HDR_OUT}')

ARGS = PARSER.parse_args()
ABSORPTION_MODEL = ARGS.absorption_model
NH = ARGS.nH
FN_ENERGY_DATA = ARGS.fn_energy_data
FN_OUT = ARGS.fn_output
LOG_FN = 'get_absorption.logging'
logging.basicConfig(filename=LOG_FN, filemode='w', level=logging.DEBUG)
logging.info(f'Command line args which were used: {ARGS}')


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


def xspec_absorption_component(ebin_min, ebin_max, fn_abs, nh=0.101):
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
    fn_abs : str
        File with implicit headers: energy (in keV), corresponding absorption component values
        Valid options - phabs_component.dat, tbabs_abund_wilm_component.dat
    nh : float
        Hydrogen column density in **units of 10^22 atoms/cm^2**
        The default 0.101 was used to create the tables phabs_component.dat and tbabs_abund_wilm_component.dat

    Returns
    -------
    array_like[float] or float
    """

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
        fn_abs = ABSORPTION_DICT[absorption_model]
        abs_bin_avg = xspec_absorption_component(ebin_min, ebin_max, fn_abs, nh)
        np.savetxt(fn_out, np.c_[energy, ebin_width, abs_bin_avg], delimiter=',', comments='',
                   header='energy_keV,ebin_width_keV,absorption')
        logging.info(f'Wrote {fn_out}')

    return None


if __name__ == "__main__":
    make_absorption_table(FN_ENERGY_DATA, ABSORPTION_MODEL, NH, FN_OUT)
