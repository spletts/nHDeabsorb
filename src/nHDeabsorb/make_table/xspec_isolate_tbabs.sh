#!/bin/bash


<<comment
Isolate TBabs component and write it to a file with header: energy (keV), tbabs (unitless; from 'model y'),
tbabs (unitless; from 'model model').
The last two columns are identical.

Run this file from with make_table/, or update paths to GRPSPEC, DAT_TBABS, etc
comment


GRPSPEC="grp_spectrum.pi"

# Units are 10^22 atoms/cm^2
# Weighted mean evaluated using https://www.swift.ac.uk/analysis/nhtot/index.php
NH=0.101


DAT_TBABS="../absorption_tables/tbabs_abund_wilm_component.dat"
ENERGYBINS="ebin_edges_100eV_to_100keV.txt"
LOG="_xspec_tbabs.log"


# Help with tcl commands and de-absorption idea (set index=0, norm=1, don't refit) supplied by Gordon, Craig A
# via the XSpec help desk email
xspec << EOF >  $LOG
`#XSPEC12>` data $GRPSPEC `#Load spectral file output from grppha`
`#XSPEC12>` ignore bad `#Ignore bad channels`
`#XSPEC12>` ignore **-0.3 `#Ignore energies below 0.3 keV`
`#XSPEC12>` ignore 10.0-** `#Ignore energies above 10 keV`
`#XSPEC12>` cpd /xw `#Set plot device`
`#XSPEC12>` setplot energy keV `#Set the x-axis to energy in keV`
`#XSPEC12>` abund wilm `#Most up to date abundances`
`#XSPEC12>` model tbabs(powerlaw) `#Absorbed power law`
`#1:tbabs:nH>` ${NH} `#Units are 10^22 atoms/cm^2`
`#2:powerlaw:PhoIndex>` `#Use default value`
`#3:powerlaw:norm>` `#Use default value`
`#XSPEC12>` freeze 1 `#Fix N_H`
`#XSPEC12>` fit
`#XSPEC12>` newpar 2
`#2:powerlaw[2]:PhoIndex:1>` 0 `#Used to de-absorb the spectra by isolating 'tbabs' component`
`#XSPEC12>` newpar 3
`#3:powerlaw[2]:norm:1>` 1 `#Used to de-absorb the spectra by isolating 'tbabs' component. Unit: ph/cm^2/s?`
`#XSPEC12>` energies $ENERGYBINS `#Set energies (by reading a file) at which to evaluate the model`
`#XSPEC12>` set energyData [tcloutr plot model x] `#To check that the energies are as expected`
`#XSPEC12>` set tbabsModelData [tcloutr plot model model] `#tbabs values`
`#XSPEC12>` set tbabsYData [tcloutr plot model y] `#tbabs values (same as above)`
`#XSPEC12>` set tbabsTable [open $DAT_TBABS w+]
`#XSPEC12>` set len [llength \$energyData]
`#XSPEC12>` puts \$tbabsTable "[lindex energy_kev 0] [lindex tbabs_nh${NH}_model_model 0] [lindex tbabs_nh${NH}_model_y 0]" `#Add header`
`#XSPEC12>`for {set idx 0} {\$idx < \$len} {incr idx} {puts \$tbabsTable "[lindex \$energyData \$idx] [lindex \$tbabsModelData \$idx] [lindex \$tbabsYData \$idx]" } `#Format file headers`
`#XSPEC12>` close \$tbabsTable
`#XSPEC12>` model clear
`#XSPEC12>` cpd none
`#XSPEC12>` quit
`#Do you really want to exit? (y)` y
EOF
