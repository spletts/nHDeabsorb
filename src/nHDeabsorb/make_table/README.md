# make_table

## About

This folder has scripts to create a table of XSpec's absorption component commands `tbabs` and `phabs` at specific energies.

If you want to change anything about the tables in [absorption_tables/](../absorption_tables/), you can do so here.

## Usage

The photoelectric absorption component $\exp(-\eta\sigma)$ can be isolated from `tbabs(powerlaw)` (or `logpar`, etc) using XSpec.
This can be used to de-absorb the X-ray spectrum.

At the advice of the XSpec help desk, I start with the XSpec model `tbabs(powerlaw)` = $\exp(-\eta_H \sigma(E) ) K E^{-\alpha}$ and perform a fit. 
(The second model does not matter because it will be set to 1). 
The modeling is done in xspec_isolate_tbabs.sh. 
Running xspec_isolate_tbabs.sh requires a grouped (with `grppha`) spectrum grp_spectrum.pi (and thus its arf and background spectrum, arf.arf and bkg.pi).

Then, in XSpec, I set $K=1$ (ph/keV/cm<sup>2</sup>) and $\alpha=0$, do **not** perform another fit, and evaluate the model at fine energy bins.
The only contribution to the model is now from `tbabs`. 
Then I write the energies and model values (using `tcloutr`: `model y` and `model model`) to a table.
The first column of this table has energies in keV. The second and third column (**identical**) have the `tbabs` component (unitless).

**Tables are made using a specific value of $\eta_H$ set in xspec_isolate_tbabs.sh**.


## Folder contents

* ebin_edges_100eV_to_100keV.txt:
    * Table with _implicit_ header: energy (in keV). These are the energies at which the absorption component is evaluated.

* make_fine_ebins_100eV_to_100keV.py
    * This script makes ebin_edges_100eV_to_100keV.txt

* arf.arf, bkg.pi, grp_spectrum.pi
    * Data needed to perform a fit in XSpec

* xspec_isolate_phabs.sh
    * Isolates Xspec's `phabs` and writes it to table saved in [absorption_tables/](../absorption_tables/)

* xspec_isolate_tbabs.sh
    * Isolates XSpec's `tbabs` with `abund wilm` and writes it to table saved in [absorption_tables/](../absorption_tables/)

* _xspec_phabs.log
    * XSpec output from running xspec_isolate_phabs.sh

* _xspec_tbabs.log
    * XSpec output from running xspec_isolate_tbabs.sh

