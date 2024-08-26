# `nH Deabsorb`


## About

This directory has scripts for isolating the photoelectric/photoionization absorption component $\exp(-\eta\sigma)$ in XSpec
and writing it to a table. 
Note $\sigma \equiv \sigma(E)$. 

This is used to deabsorb a spectrum by dividing the observed flux by the absorption component.

## Usage

The output of this repo is `fn_output`, which is a table that contains the absorption component in specific energy bins.

```powershell
[nHDeabsorb]$  python get_absorption.py --help
usage: get_absorption.py [-h] [--fn_output FN_OUTPUT] absorption_model nH fn_energy_data

Evaluate the photoionization absorption component given specific energy bins (in keV)

positional arguments:
  absorption_model      Valid options are: dict_keys(['phabs', 'tbabs_abdund_wilm']).
  nH                    Hydrogen column density in units of 10^22 1/cm^2.
  fn_energy_data        Filename of data file which contains the energy bin centers (in keV) in the first column,
                        and the energy bin width (in keV) in the second column. This file must not have a header
                        (to change this behavior edit `skip_header`). This file can have any number of columns, as
                        only the first two are read.

optional arguments:
  -h, --help            show this help message and exit
  --fn_output FN_OUTPUT
                        Filename of output data file which contains the energy bin centers (in keV) in the first
                        column, and the energy bin width (in keV) in the second column, and the corresponding
                        absorption component in the third a nd final column. This comma-separated file has header
                        energy_keV,ebin_width_keV,absorption
```

Reiterating the above:

There are three required command line args (`absorption_model nH fn_energy_data`) 
and one optional command line arg `fn_output`:
* `absorption_model`: which absorption model to apply.
  * Valid options are `'phabs', 'tbabs_abdund_wilm'`
    * `tbabs` with `abund wilm` is the photoelectric absorption component $\exp(-\eta\sigma)$ using the Tuebingen-Boulder ISM absorption model and ISM abundances from [`wilm`](https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract).
* `nH`: Hydrogen column density **in units of 10^22 cm<sup>-2</sup>**.
  * The files 'tbabs_abund_wilm_component.dat' and 'phabs_component.dat' in this directory use $\eta_H = 0.101 \times 10^{22}$ 1/cm<sup>2</sup>
* `fn_energy_data`: filename for SED data which must have
  * No header (to change this behavior, edit `skip_header` in `make_absorption_table`)
  * Energy in keV in the first column (to change this requirement, edit `energy = data[:, 0]` with the relevant index in `make_absorption_table`)
  * Energy bin width in keV in the second column (to change this requirement, edit `ebin_width = data[:, 1]` with the relevant index in `make_absorption_table`)
  * Note that the remaining columns are not read.
* `fn_output`: the default is `absorption.csv`
  * Filename of output data file which contains the energy bin centers (in keV) in the first
                        column, and the energy bin width (in keV) in the second column, and the corresponding
                        absorption component in the third a nd final column. This comma-separated file has header
                        energy_keV,ebin_width_keV,absorption
## Example

Run the following command in the directory `nHDeabsorb`, which will create `absorption.csv`

```shell
[nHDeabsorb]$  python get_absorption.py tbabs_abund_wilm 0.157 sample_sed.dat
```

---

### Folder contents

`tbabs_abund_wilm_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **TBabs component with `abund wilm`** is evaluated at. These are from `ebin_edges.txt`.
  * `tbabs_nh{NH}_model_model`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `tbabs_nh{NH}_model_y`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}`. `tbabs_nh{NH}_model_model` and `tbabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`phabs_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **phabs** component is evaluated at. These are from `ebin_edges.txt`.
  * `phabs_nh{NH}_model_model`: **phabs** component calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `phabs_nh{NH}_model_y`: **phabs** component calculated using fixed `{NH}`. `phabs_nh{NH}_model_model` and `phabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`sample_sed.dat`:
* Data table with implicit header: energy (keV), energy half bin width (keV), energy flux (keV/cm<sup>2</sup>/s), energy flux error (keV/<sup>2</sup>/s), model energy flux (keV/<sup>2</sup>/s)

---

### User-specified nH

#### Option 1 
To evaluate `tbabs` at a different value, you can set `NH` in `make_tables/xspec_isolate_tbabs.sh` and rerun `xspec_isolate_tbabs.sh` (via `./xspec_isolate_tbabs.sh`) to rewrite the file `tbabs_component.dat`.

#### Option 2
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

