Usage
=====

The user has observed fluxes :math:`F_{obs}` fit with XSpec using the XSpec command ``phabs`` or ``tbabs`` + ``abund wilm``.
To get the intrinsic flux :math:`F_{int} = F_{obs}/\exp(-\eta\sigma)`, the absorption :math:`\exp(-\eta\sigma)` must be isolated.
There are two ways to retrieve the absorption, use whichever works better with your workflow:
                             
* Retrieve the absorption values directly as an array with ``get_absorption.xspec_absorption_component``
* Get the absorption values as a table with ``get_absorption.make_absorption_table``

Example
-------

Package use
~~~~~~~~~~~
If the package is installed (as in :ref:`Installing from source`), to get an array of absorption values (below is a file in example_scripts/):

.. literalinclude:: ../example_scripts/pkg_run_arr.py
   :language: python

where (also see function docstring ):

* ``ebin_min``, ``ebin_max`` : lower, upper bin edges in *keV*.
* ``absorption_model``: which absorption model from XSpec to apply. Valid options are 'phabs', 'tbabs_abdund_wilm'

    * 'phabs': XSpec's ``phabs`` command
    * 'tbabs_abdund_wilm': XSpec's ``tbabs`` command with ``abund wilm`` set. This is the photoelectric absorption component :math:`\exp(-\eta\sigma)` using the Tuebingen-Boulder ISM absorption model and ISM abundances from `wilm <https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract>`_.
* ``calc_avg_using_endpoints=False`` :  Calculates the absorption in each bin by averaging all the absorption values that lie within each bin.
* ``nh``: Hydrogen column density in units of 10 :sup:`22` cm :sup:`-2` used for your XSpec analysis

To save the values to a table (below is a file in example_scripts/)::

.. literalinclude:: ../example_scripts/pkg_run_tbl.py
   :language: python

where (also see function docstring):

* ``fn_sed_data``: filename for SED data which must have:

    * No header (to change this behavior, edit ``skip_header`` in get_absorption.make_absorption_table)
    * Energy in keV in the first column (to change this requirement, edit ``energy = data[:, 0]`` with the relevant index)
    * Energy bin width in keV in the second column (to change this requirement, edit ``ebin_width = data[:, 1]``)
    * Note that the remaining columns are not read.
* ``absorption_model``: which absorption model from XSpec to apply. Valid options are 'phabs', 'tbabs_abdund_wilm'

    * 'phabs': XSpec's ``phabs`` command
    * 'tbabs_abdund_wilm': XSpec's ``tbabs`` command with ``abund wilm`` set. This is the photoelectric absorption component :math:`\exp(-\eta\sigma)` using the Tuebingen-Boulder ISM absorption model and ISM abundances from `wilm <https://ui.adsabs.harvard.edu/abs/2000ApJ...542..914W/abstract>`_.
* ``nh``: Hydrogen column density in units of 10 :sup:`22` cm :sup:`-2` used for your XSpec analysis
* ``calc_avg_using_endpoints=False`` :  Calculates the absorption in each bin by averaging all the absorption values that lie within each bin.
* ``fn_out``:  filename of output data file which contains the energy bin centers (in keV) in the first column, and the energy bin width (in keV) in the second column, and the corresponding absorption component in the third and final column. This comma-separated file has explicit header: energy_keV,ebin_width_keV,absorption.
