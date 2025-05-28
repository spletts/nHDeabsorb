Features and Overview
=====================

Main feature: quantify absorption of X-rays
-------------------------------------------

Given user-set energy bins (in keV), returns the photoelectric/photoionization absorption :math:`\exp(-\eta\sigma(E))`, 
as calculated by XSpec (``tbabs`` + ``abund wilm``, ``phabs``). This depends on the details of the user's XSpec analysis:

* Which absorption model was used (``tbabs`` + ``abund wilm``, ``phabs`` are supported (see `Make tables` if you use a different absorption model)
* Which nH value was used
* User-set energy bins should be from the SED output by XSpec


.. _Make tables:

Make absorption tables
----------------------
Tables in this repository (`absorption_tables/ <https://github.com/spletts/nHDeabsorb/src/nHDeabsorb/absorption_tables>`_) were created using XSpec.
The tables contain the absorption :math:`\exp(-\eta\sigma(E))` 
(where :math:`\eta` is `nH` the Hydrogen column density, and :math:`\sigma(E)` is the cross section) and corresponding energy (in keV). 
This is done to indirectly access whichever formula for the cross section that XSpec uses for each model. 
The table is interpolated in order to evaluate the nH absorption at specific energies, outside of XSpec.
    
    * The absorption component was isolated for XSpec's ``tbabs`` + ``abund wilm`` and ``phabs`` commands/models.
    * Plot of absorption tables used in the repository:

    .. image:: ../src/nHDeabsorb/absorption_plots/absorption_vs_xrt_energy_range.png
       :alt: Absorption vs energy plot of tables used in the repository
  
If desired the user can make their own absorption tables (e.g. for models not included here) by editing the code in `make_table/ <https://github.com/spletts/nHDeabsorb/src/nHDeabsorb/make_table>`_
  
Deabsorb spectra
----------------
To determine the intrinsic/deabsorbed flux from the observed flux, divide the observed flux by the absorption: :math:`F_{int} = F_{obs}/\exp(-\eta\sigma)`. 
This package calculates :math:`\exp(-\eta\sigma)`.
Intrinsic emission is required input for blazar modeling codes such as Bjet_MCMC.

To evaluate the absorption of a source at redshift :math:`z` (e.g. XSpec's ``zphabs``), evaluate :math:`\sigma(E)` at :math:`E(1+z)` and use the intrinsic nH (not Galactic nH). 
For details see the XSpec User Guide's documentation for ``zphabs``.

User-set nH
-----------

The absorption is energy and nH (Hydrogen column density) dependent. 
The user can set ``nh`` (this is done in units of 10 :sup:`22` cm :sup:`-2`). 
The tables (e.g. tbabs_abund_wilm_component.dat) have absorption :math:`p_1` (column name "tbabs_nh0.101_model_mode") for :math:`\eta_1 = 0.101` (units of 10 :sup:`22` cm :sup:`-2`). 
This repository calculates absorption :math:`p_2` for :math:`\eta_2` (``nh``) via:

.. math::

  p_1 = \exp( -\eta_1 \sigma(E) ) \Rightarrow \sigma(E) = - \frac{\ln(p_1)}{\eta_1}

  p_2 = \exp( -\eta_2 \sigma(E) ) = p_1^{\eta_2/\eta_1}
