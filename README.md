# `nH Deabsorb`


## About

This directory has scripts for isolating the photoelectric absorption component $\exp(-\eta\sigma)$ in XSpec. 
Note $\sigma \equiv \sigma(E)$. 

This is used to deabsorb a spectrum.

## Usage

Call the function `get_absorption.xspec_absorb_component(ebin_min, ebin_max, fn_abs, nh=0.101)`:

`ebin_min, ebin_max` are lists/arrays of the lower, upper bin edges in *keV* (respectively).

`fn_abs` is either 'tbabs_component.dat' or 'phabs_component.dat'. 
Use 'phabs_component.dat' if you used `phabs` in XSpec. 
Use 'tbabs_component.dat' if you used `tbabs` with `abund wilm` in XSpec. 
`tbabs` with `abund wilm`** which is the photoelectric absorption component $\exp(-\eta\sigma)$ using the Tuebingen-Boulder ISM absorption model and ISM abundances from [`wilm`](https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract).

`nh` is the Hydrogen column density in units of $10^{22}$ cm<sup>-2</sup>. 
The files 'tbabs_component.dat' and 'phabs_component.dat' in this directory use $\eta_H = 0.101 \times 10^{22}$ 1/cm<sup>2</sup>, 
so the default for `nh` is 0.101. 
For using a nondefault `nh` see [User-specified nH](#User-specified-nH).

Note: according to the XSpec help desk (xspec12@athena.gsfc.nasa.gov): 
"Tbabs evaluates the cross-section at each end of the energy bin and averages them." 
So this function does the same. 
The absorption is evaluated at each end of the energy bin via interpolation of the table in `fn_abs`.

---

### Folder contents

`tbabs_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **TBabs component with `abund wilm`** is evaluated at. These are from `ebin_edges.txt`.
  * `tbabs_nh{NH}_model_model`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `tbabs_nh{NH}_model_y`: **TBabs component (with `abund wilm`)** calculated using fixed `{NH}`. `tbabs_nh{NH}_model_model` and `tbabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`phabs_component.dat`:
* Table with explicit headers: 
  * `energy_kev`: Energies in keV at which the **phabs** component is evaluated at. These are from `ebin_edges.txt`.
  * `tbabs_nh{NH}_model_model`: **phabs** component calculated using fixed `{NH}` (a placeholder for the $\eta_H$ set in `make_tables/xspec_isolate_tbabs.sh`)
  * `tbabs_nh{NH}_model_y`: **phabs** component calculated using fixed `{NH}`. `tbabs_nh{NH}_model_model` and `tbabs_nh{NH}_model_y` should be identical; the first uses XSpec's `tcloutr` with `model model` command to get the model values and the second uses `model y`. 

`get_absorption.py`:
* Script to isolate the absorption component. Also makes a plot of the isolated absorption component `plot_of_absorption.png`.

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

The `tbabs` component can be evaluated as $\exp( -\eta_1 \sigma(E) )$ using the above equation for $\sigma(E)$:

$p_2 = p_1^{\eta_2/\eta_2}$

## Acknowledgements

* Craig A. Gordon from the XSpec help desk provided instructions to isolate the absorption component. He also wrote a sample tcl script (via email exchange) to write values to data tables within XSpec.

