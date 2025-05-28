Installation
============

Clone and edit PYTHONPATH
-------------------------

This is a very light package.
If you prefer you can simply clone the repository and reorganize the necessary handful of functions and files into your own already-existing analysis pipelines,
which likely already have the `Requirements`_.
You can add it to your PYTHONPATH :``export PYTHONPATH=$PYTHONPATH:/path/to/nHDeabsorb/src/nHDeabsorb``;
now you should be able to ``from nHDeabsorb import get_absorption``.
**However**, you may need to edit the path to `absorption_tables/ <https://github.com/spletts/nHDeabsorb/src/nHDeabsorb/absorption_tables>`_ in the source code (get_absorption.py), specifically lines with ``pkg_resources.resource_filename``.


.. _Installing from source:

Installing from source
---------------------------

.. code:: bash

   git clone https://github.com/spletts/nHDeabsorb.git
   cd nHDeabsorb
   python -m build
   pip install dist/nhdeabsorb-0.2.0-py3-none-any.whl


(I believe the lowercase nhdeabsorb in the filename is due the version of setuptools or build; it may be uppercase as nHDeabsorb for other versions of setuptools).

Or use edit mode

.. code:: bash

  git clone https://github.com/spletts/nHDeabsorb.git
  cd nHDeabsorb
  pip install -e .


Now you can ``import nHDeabsorb``.

.. _Requirements:

Requirements
-----------------

* setuptools
* `Non-conflicting versions <https://docs.scipy.org/doc/scipy-1.15.2/dev/toolchain.html>`_ of numpy, scipy, and Python

    * e.g. numpy>=1.21.6,<1.27.0, scipy>=1.11,<1.12, python>=3.9,<3.13
* Python>=3 due to string formatting ``f{}``
