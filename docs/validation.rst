Validation
==========

The plots in this folder contain 'XSpec model' (absorbed powerlaw) and 'nHDeabsorb' (powerlaw evaluated using XSpec's best fit parameters, absorption evaluated using nHDeabsorb in two ways).
These are expected to match very closely.

'XSpec model' is the value of the model which is calculated by XSpec: M(E) A(E), where M(E) is the absorption model and A(E) is the intrinsic spectrum (e.g. powerlaw in all cases in this folder).
There are no errors on this value reported by XSpec with the tcloutr command.

'nHDeabsorb' is the absorption model M(E) evaluated with nHDeabsorb in two ways (1. averaging the value at the bin endpoints, and 2. averaging over all points in the absorption table within the bin), and A(E) evaluated with the best fit parameters determined by XSpec.

    .. image:: ../src/nHDeabsorb/validation/sed_eflux_00032646001.png
       :alt: Plot of fluxes vs energy and residuals vs energy for ObsID 00032646001, for validation

    .. image:: ../src/nHDeabsorb/validation/sed_eflux_00041535055.png
       :alt: Plot of fluxes vs energy and residuals vs energy for ObsID 00041535055, for validation

A few more plots like these are on GitHub.
