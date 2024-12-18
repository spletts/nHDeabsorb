# `nH Deabsorb`


## About

This package has scripts for isolating the **Galactic** photoelectric/photoionization absorption component $\exp(-\eta\sigma)$ 
in the range 0.3-10 keV in XSpec and writing it to a table. 
Note $\sigma \equiv \sigma(E)$.
To evaluate intrinsic absorption, evaluate $\sigma(E)$ at $E(1+z)$ (as described in the XSpec Manual Sec 6.3.24). 

This is used to deabsorb a spectrum by dividing the observed flux by the absorption component.

## Install and Requirements

This is a very light package. You can pull the repository and implement it into your own already-existing analysis pipelines. You should only need parts of the following files (take care to update the paths and imports):
* src/nHDeabsorb/get_absorption.py
* src/nHDeabsorb/phabs_component.dat or src/nHDeabsorb/tbabs_abund_wilm_component.dat

Or you can use it as a package by pulling the repo and 
```
python -m build
pip install dist/nHDeabsorb-0.1.0-py3-none-any.whl
```

Requirements: 

* Python 3 (uses `f'{variable_name}'` string formatting)
* numpy<=1.25.2. There are some numpy and scipy version conflicts which are the reason for this numpy version.

## Usage and Example

The output of this repo is `fn_out`: Filename of output data file which contains the energy bin centers (in keV) in the first column, and the energy bin width
                        (in keV) in the second column, and the corresponding absorption component in the third and final column. This comma-
                        separated file has explicit header energy_keV,ebin_width_keV,absorption. 

Example:
```powershell
 [nHDeabsorb]$  python call_get_absorption.py
```

This script calls `get_absorption.make_absorption_table`. See the docstring for parameter definitions, but they are also below:
* `absorption_model`: which absorption model from XSpec to apply.
  * Valid options are `'phabs', 'tbabs_abdund_wilm'`
    * `phabs`: XSpec's `phabs` command
      * `tbabs` with `abund wilm`: XSpec's `tbabs` command with `abund wilm` set. This is the photoelectric absorption component $\exp(-\eta\sigma)$ using the Tuebingen-Boulder ISM absorption model and ISM abundances from [`wilm`](https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract).
* `nh`: Hydrogen column density **in units of 10<sup>22</sup> cm<sup>-2</sup>**.
  * The files 'tbabs_abund_wilm_component.dat' and 'phabs_component.dat' in this directory use $\eta_H = 0.101 \times 10^{22}$ 1/cm<sup>2</sup>
* `fn_sed_data`: filename for SED data which must have:
  * No header (to change this behavior, edit `skip_header` in `make_absorption_table`)
  * Energy in keV in the first column (to change this requirement, edit `energy = data[:, 0]` with the relevant index in `make_absorption_table`)
  * Energy bin width in keV in the second column (to change this requirement, edit `ebin_width = data[:, 1]` with the relevant index in `make_absorption_table`)
  * Note that the remaining columns are not read.
* `fn_out`: the default is `absorption.csv`
  * Filename of output data file which contains the energy bin centers (in keV) in the first
                        column, and the energy bin width (in keV) in the second column, and the corresponding
                        absorption component in the third and final column. Energies outside the range 0.3-10 keV have absorption=1 (corresponding to no absorption). 
                        This comma-separated file has explicit ^header: energy_keV,ebin_width_keV,absorption.

---

### Folder contents

`src/nHDeabsorb/tbabs_abund_wilm_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **TBabs component with `abund wilm`** is evaluated at. These are from `ebin_edges.txt`.
  * `tbabs_nh{NH}_model_model`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `tbabs_nh{NH}_model_y`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}`. `tbabs_nh{NH}_model_model` and `tbabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`src/nHDeabsorb/phabs_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **phabs** component is evaluated at. These are from `ebin_edges.txt`.
  * `phabs_nh{NH}_model_model`: **phabs** component calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `phabs_nh{NH}_model_y`: **phabs** component calculated using fixed `{NH}`. `phabs_nh{NH}_model_model` and `phabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`src/nHDeabsorb/sample_sed.dat`:
* Data table with implicit header: energy (keV), energy half bin width (keV), energy flux (keV/cm<sup>2</sup>/s), energy flux error (keV/<sup>2</sup>/s), model energy flux (keV/<sup>2</sup>/s)

---

### User-specified nH

#### Option 1 
To evaluate `tbabs` at a different value, you can set `NH` in `src/nHDeabsorb/make_tables/xspec_isolate_tbabs.sh` and rerun `xspec_isolate_tbabs.sh` (via `./xspec_isolate_tbabs.sh`) to rewrite the file `tbabs_component.dat`.

#### Option 2 (implemented in this repo)
The user can set `nh` in `get_absorption.xspec_absorb_component(ebin_min, ebin_max, fn_abs, nh=0.101)`
(in units of $10^{22}$ cm<sup>-2</sup>).

To evaluate `tbabs` at a different value $\eta_2$ using the table `tbabs_component.dat` as is, 
let $p_1$ be the value of `tbabs` that is in the table `tbabs_component.dat` (second column) 
which was created using $\eta_1$.

$p_1 = \exp( -\eta_1 \sigma(E) )$ where $\eta_1 = 0.101 \times 10^{22}$ 1/cm<sup>2</sup>.

$\Rightarrow \sigma(E) = - \frac{\ln(p_1)}{\eta_1}$

The `tbabs` component can be evaluated as $p_2 = \exp( -\eta_2 \sigma(E) )$ using the above equation for $\sigma(E)$:

$p_2 = p_1^{\eta_2/\eta_1}$

## Acknowledgements

* Craig A. Gordon from the XSpec help desk provided instructions to isolate the absorption component. He also wrote a sample tcl script (via email exchange) to write values to data tables within XSpec.

