#!/bin/bash

GRP_SPEC="grp_spectrum.pi"
OUT_DIR="powlaw_tbabs"

# Units are 10^22 atoms/cm^2
# Weighted mean evaluated using https://www.swift.ac.uk/analysis/nhtot/index.php
NH_TBABS=0.157


PARAM_TBL="${OUT_DIR}/param_tbl.dat"
STAT_TBL="${OUT_DIR}/stat_tbl.dat"
UNBINNED_DATA_TBL_PHFLUX="${OUT_DIR}/spec_default_bin_ufspec.dat"
UNBINNED_DATA_TBL_EFLUX="${OUT_DIR}/spec_default_bin_eeufspec.dat"
LOG_XSPEC="_xspec_tbabs.log"


xspec << EOF > ${OUT_DIR}/${LOG_XSPEC}
`#XSPEC12>` data $GRP_SPEC `#Load spectral file formatted as...`
`#XSPEC12>` ignore bad `#Ignore bad channels`
`#XSPEC12>` ignore **-0.3 `#Ignore energies below 0.3 keV`
`#XSPEC12>` ignore 10.0-** `#Ignore energies above 10 keV`
`#XSPEC12>` cpd /xw `#Set plot device`
`#XSPEC12>` setplot energy keV `#Set the x-axis to energy in keV`
`#XSPEC12>` abund wilm `#Most up to date`
`#XSPEC12>` model tbabs(powerlaw) `#Absorbed power law`
`#1:tbabs:nH>` $NH_TBABS `#Units are 10^22 atoms/cm^2`
`#2:powerlaw:PhoIndex>` `#Use default value`
`#3:powerlaw:norm>` `#Use default value`
`#XSPEC12>` freeze 1 `#Fix N_H`
`#XSPEC12>` fit
`#XSPEC12>` save all $OUT_DIR/fit `#Save all XSpec commands up to this point`

`#XSPEC12>` error 1. 2-3 `#1 sigma range..? for parameters 2-3`
`#XSPEC12>` flux 2 10 err `#Calc integral flux between 2-10 keV and the 68% confidence interval (flux with absorption)`
`#XSPEC12>` set parFlux [tcloutr flux] `#6 values: val errLow errHigh (in ergs/cm2) val errLow errHigh (in photons)`
`#XSPEC12>` set parIndex [tcloutr param 2] `#Term in brackets returns: 'value, delta, min, low, high, max' for parameter 2`
`#XSPEC12>` set parIndexErr [tcloutr error 2] `#'Writes last confidence region calculated'. This is 1sigma if this was the previously specified error. If everything went well, the error string should be FFFFFFFFF. 'tcloutr error 1. 2' results in no output`
`#XSPEC12>` set parNorm [tcloutr param 3]
`#XSPEC12>` set parNormErr [tcloutr error 3]
`#XSPEC12>` set rateEtc [tcloutr rate all] `#Count rate, uncertainty, model rate, and percentage of net flux (no background) compared to total flux`
`#XSPEC12>` set cRate [lindex \$rateEtc 0] `#Count rateEtc...`
`#XSPEC12>` set cRateErr [lindex \$rateEtc 1]
`#XSPEC12>` set cRateLow [expr {\$cRate - \$cRateErr}]
`#XSPEC12>` set cRateHigh [expr {\$cRate + \$cRateErr}]
`#XSPEC12>` set paramTable [open $PARAM_TBL w+]
`#XSPEC12>` puts \$paramTable "[lindex name 0] [lindex param 0] [lindex param_low 0] [lindex param_high 0] [lindex error_string 0]" `#Add header`
`#XSPEC12>` puts \$paramTable "[lindex PhoIndex 0] [lindex \$parIndex 0] [lindex \$parIndexErr 0] [lindex \$parIndexErr 1] [lindex \$parIndexErr 2]" `#0th index of parIndex contains 'value'. 0th index of parIndexErr has the lower bound on the parameter, 1st has upper bound.`
`#XSPEC12>` puts \$paramTable "[lindex norm 0] [lindex \$parNorm 0] [lindex \$parNormErr 0] [lindex \$parNormErr 1] [lindex \$parNormErr 2]" `#Write 3rd row of table`
`#XSPEC12>` puts \$paramTable "[lindex flux 0] [lindex \$parFlux 3] [lindex \$parFlux 4] [lindex \$parFlux 5] [lindex 0 0]"
`#XSPEC12>` puts \$paramTable "[lindex countrate 0] [lindex \$cRate 0] [lindex \$cRateLow 0] [lindex \$cRateHigh 0] [lindex 0 0]"
`#XSPEC12>` close \$paramTable
`#XSPEC12>` set nullProb [tcloutr nullhyp] `#Null hypothesis probability. 'If this probability is small then the model is not a good fit.'`
`#XSPEC12>` set chiSq [tcloutr stat] `#Value of fit statistic. In this file, Fit statistic  : Chi-Squared`
`#XSPEC12>` set dof [tcloutr dof] `#Degrees of freedom in fit, and the number of channels.`
`#XSPEC12>` set statTable [open $STAT_TBL w+]
`#XSPEC12>` puts \$statTable "[lindex chi_squared 0] [lindex deg_freedom 0] [lindex null_hyp_probability 0]" `#Add header`
`#XSPEC12>` puts \$statTable "[lindex \$chiSq 0] [lindex \$dof 0] [lindex \$nullProb 0]"
`#XSPEC12>` close \$statTable

`#XSPEC12>` plot model ufspec 
`#XSPEC12>` setplot command rescale 0.3 10 
`#XSPEC12>` plot model ufspec 
`#XSPEC12>` set xDataEnergy [tcloutr plot ufspec x] 
`#XSPEC12>` set xDataEnergyErr [tcloutr plot ufspec xerr] 
`#XSPEC12>` set yDataEFlux [tcloutr plot ufspec y] 
`#XSPEC12>` set yDataEFluxErr [tcloutr plot ufspec yerr]
`#XSPEC12>` set modelDataEFlux [tcloutr plot ufspec model]
`#XSPEC12>` set unbinDataTable [open $UNBINNED_DATA_TBL_PHFLUX w+]
`#XSPEC12>` set len [llength \$xDataEnergy] 
`#XSPEC12>` for {set idx 0} {\$idx < \$len} {incr idx} {puts \$unbinDataTable "[lindex \$xDataEnergy \$idx] [lindex \$xDataEnergyErr \$idx] [lindex \$yDataEFlux \$idx] [lindex \$yDataEFluxErr \$idx] [lindex \$modelDataEFlux \$idx]" } 
`#XSPEC12>` close \$unbinDataTable

`#XSPEC12>` plot eemodel eeufspec 
`#XSPEC12>` setplot command rescale 0.3 10 
`#XSPEC12>` plot eemodel eeufspec 
`#XSPEC12>` set xDataEnergy [tcloutr plot eeufspec x] 
`#XSPEC12>` set xDataEnergyErr [tcloutr plot eeufspec xerr] 
`#XSPEC12>` set yDataEFlux [tcloutr plot eeufspec y] 
`#XSPEC12>` set yDataEFluxErr [tcloutr plot eeufspec yerr]
`#XSPEC12>` set modelDataEFlux [tcloutr plot eeufspec model]
`#XSPEC12>` set unbinDataTable [open $UNBINNED_DATA_TBL_EFLUX w+]
`#XSPEC12>` set len [llength \$xDataEnergy] 
`#XSPEC12>` for {set idx 0} {\$idx < \$len} {incr idx} {puts \$unbinDataTable "[lindex \$xDataEnergy \$idx] [lindex \$xDataEnergyErr \$idx] [lindex \$yDataEFlux \$idx] [lindex \$yDataEFluxErr \$idx] [lindex \$modelDataEFlux \$idx]" } 
`#XSPEC12>` close \$unbinDataTable

`#XSPEC12>` model clear
`#XSPEC12>` cpd none
`#XSPEC12>` quit
`#Do you really want to exit? (y)` y
EOF