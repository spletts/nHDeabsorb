# nHDeabsorb


## Overview

nHDeabsorb is designed for use with [XSpec](https://xspec.io)-produced X-ray spectra in order to determine the intrinsic X-ray emission by nH-deabsorbing spectra. This is required for blazar SED modeling codes such as [Bjet_MCMC](https://bjet-mcmc.readthedocs.io/en/latest/) which model the intrinsic (not observed) emission.

## Installation

### Clone and edit PYTHONPATH

This is a very light package. 
If you prefer you can simply clone the repository and reorganize the necessary handful of functions and files into your own already-existing analysis pipelines, 
which likely already have the [required packages](#requirements).
You can add it to your PYTHONPATH `export PYTHONPATH=$PYTHONPATH:/path/to/nHDeabsorb/src/nHDeabsorb`; now you should be able to `from nHDeabsorb import get_absorption`.
**However**, you may need to edit the path to [absorption_tables/](src/nHDeabsorb/absorption_tables/) in the [source code](src/nHDeabsorb/get_absorption.py), specifically lines with `pkg_resources.resource_filename`.

### Installing from source

```shell
git clone https://github.com/username/nHDeabsorb.git
cd nHDeabsorb
python -m build
pip install dist/nhdeabsorb-0.2.0-py3-none-any.whl
```
(I believe the lowercase of nhdeabsorb in the filename is due the version of setuptools or build; it may be uppercase as nHDeabsorb for other versions of setuptools).
or edit mode
```shell
git clone https://github.com/username/nHDeabsorb.git
cd nHDeabsorb
pip install -e .
```

Now you can `import nHDeabsorb`.

python -m build

### Requirements

* setuptools
* numpy, scipy, and Python [non-conflicting versions](https://docs.scipy.org/doc/scipy-1.15.2/dev/toolchain.html) 
  * e.g. numpy>=1.21.6,<1.27.0, scipy>=1.11,<1.12, python>=3.9,<3.13
* Python>=3 due to string formatting `f{}`


## Context

* Main feature: Given user-set energy bins (in keV), returns the photoelectric/photoionization absorption $\exp(-\eta\sigma(E))$, as calculated by XSpec (`tbabs` + `abund wilm`, `phabs`). This depends on the details of the user's XSpec analysis:
  * Which absorption model was used (`tbabs` + `abund wilm`, `phabs` are supported, but user should be able to implement other models using [make_table/](src/nHDeabsorb/make_table/))
  * Which nH value was used
  * User-set energy bins should be from the SED output by XSpec
* Tables in this repository ([absorption_tables/](src/nHDeabsorb/absorption_tables/)) were created using XSpec. The tables contain the absorption $\exp(-\eta\sigma)$ (where $\sigma \equiv \sigma(E)$, $\eta$ is `nH`, and $\sigma(E)$ is the cross section) and corresponding energy (in keV).  This is done to indirectly access whichever formula for the cross section that XSpec uses for each model. The table is interpolated in order to evaluate the nH absorption at specific energies, outside of XSpec.
  * The absorption component was isolated for XSpec's `tbabs` + `abund wilm` and `phabs` commands/models.
  * [Plot of absorption tables used in the repository](src/nHDeabsorb/absorption_plots/absorption_vs_xrt_energy_range.png)  
* To determine the intrinsic/deabsorbed flux from the observed flux, divide the observed flux by the absorption: $F_{int} = F_{obs}/\exp(-\eta\sigma)$. This package calculates $\exp(-\eta\sigma)$.
  * Intrinsic emission is required input for blazar modeling codes such as Bjet_MCMC.
* To evaluate intrinsic absorption of a source at redshift $z$ (e.g. XSpec's `zphabs`), evaluate $\sigma(E)$ at $E(1+z)$. For details see the XSpec User Guide's documentation for `zphabs`.

* The absorption is energy and nH (Hydrogen column density) dependent. The user can set `nh` (this is done in units of $10^{22}$ cm<sup>-2</sup>). The tables (e.g. [tbabs_abund_wilm_component.dat](src/nHDeabsorb/absorption_tables/tbabs_abund_wilm_component.dat)) have absorption $p_1$ (column name "tbabs_nh0.101_model_mode") for $\eta_1 = 0.101$ (units of $\times 10^{22}$ atoms cm<sup>-2</sup>). This repository calculates absorption $p_2$ for $\eta_2$ (`nh`) via:
    
    $p_1 = \exp( -\eta_1 \sigma(E) ) \Rightarrow \sigma(E) = - \frac{\ln(p_1)}{\eta_1}$
    
    $p_2 = \exp( -\eta_2 \sigma(E) ) = p_1^{\eta_2/\eta_1}$

## Usage 

The user has observed fluxes $F_{obs}$ fit with XSpec using the XSpec command `phabs` or `tbabs` + `abund wilm`.
To get the intrinsic flux $F_{int} = F_{obs}/\exp(-\eta\sigma)$, the absorption $\exp(-\eta\sigma)$ must be isolated.
There are two ways to retrieve the absorption, use whichever works better with your workflow:
* Retrieve the absorption values directly as an array with `get_absorption.xspec_absorption_component`
* Get the absorption values as a table with `get_absorption.make_absorption_table`

**Note**: XSpec computes the absorption in each energy bin by taking the average absorption of the bin edges. Thus, this script does the same. 
If you want to calculate the absorption at a specific energy (not across a bin), use `get_absorption.interpolate_absorption`.

### Example

If the package is installed (as in [installing from source](#installing-from-source)):
```python
from nHDeabsorb import get_absorption

# One option: get the absorption values as array, using array of energies
absorb = get_absorption.xspec_absorption_component(ebin_min=[0.4, 0.5], 
                                                ebin_max=[0.5, 0.6], 
                                                absorption_model='tbabs_abund_wilm',
                                                nh=0.15)
```
where (also see function docstring):
* `ebin_min`, `ebin_max` : lower, upper bin edges in *keV*.
* `absorption_model`: which absorption model from XSpec to apply. Valid options are `'phabs', 'tbabs_abdund_wilm'`
    * `phabs`: XSpec's `phabs` command
    * `tbabs` with `abund wilm`: XSpec's `tbabs` command with `abund wilm` set. This is the photoelectric absorption component $\exp(-\eta\sigma)$ using the Tuebingen-Boulder ISM absorption model and ISM abundances from [`wilm`](https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract).
* `nh`: Hydrogen column density **in units of 10<sup>22</sup> cm<sup>-2</sup>** used for your XSpec analysis 


```python
from nHDeabsorb import get_absorption

# Another option: get the absorption values as table, using table which contains energies
fn_spec = pkg_resources.resource_filename('nHDeabsorb', 'sample_data/sed.dat')
absorb_for_spec = get_absorption.make_absorption_table(fn_sed_data=fn_spec, 
                                                    absorption_model='tbabs_abund_wilm', 
                                                    nh=0.15, 
                                                    fn_out='../absorption_values.csv')
```
where (also see function docstring):
* `fn_sed_data`: filename for SED data which must have:
  * No header (to change this behavior, edit `skip_header` in `make_absorption_table`)
  * Energy in keV in the first column (to change this requirement, edit `energy = data[:, 0]` with the relevant index)
  * Energy bin width in keV in the second column (to change this requirement, edit `ebin_width = data[:, 1])
  * Note that the remaining columns are not read.
* `absorption_model`: which absorption model from XSpec to apply. Valid options are `'phabs', 'tbabs_abdund_wilm'`
    * `phabs`: XSpec's `phabs` command
    * `tbabs` with `abund wilm`: XSpec's `tbabs` command with `abund wilm` set. This is the photoelectric absorption component $\exp(-\eta\sigma)$ using the Tuebingen-Boulder ISM absorption model and ISM abundances from [`wilm`](https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract).
* `nh`: Hydrogen column density **in units of 10<sup>22</sup> cm<sup>-2</sup>** used for your XSpec analysis 
* `fn_out`:  filename of output data file which contains the energy bin centers (in keV) in the first
                        column, and the energy bin width (in keV) in the second column, and the corresponding
                        absorption component in the third and final column.
                        This comma-separated file has explicit header: energy_keV,ebin_width_keV,absorption.


If not installed with pip, update the imports necessary to call `xspec_absorption_component` and/or `make_absorption_table`. Everything else follows as above.


## License

3-Clause BSD License; see [LICENSE](LICENSE).

## References and Acknowledgements

* [Arnaud, K. A., “XSPEC: The First Ten Years”](https://ui.adsabs.harvard.edu/abs/1996ASPC..101...17A/abstract)

* Craig A. Gordon from the XSpec help desk provided instructions to isolate the absorption component. He also wrote a sample tcl script (via email exchange) to write values to data tables within XSpec.

