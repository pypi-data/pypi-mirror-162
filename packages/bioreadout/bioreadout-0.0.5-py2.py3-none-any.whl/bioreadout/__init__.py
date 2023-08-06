"""Bio file readers, instrument schema.

Import the package::

   import bioreadout

This is the complete API reference:

.. autosummary::
   :toctree: .

   readout_type
"""

__version__ = "0.0.5"  # denote a pre-release for 0.1.0 with 0.1a1

from . import lookup  # noqa
from ._efo import EFO, readout_type  # noqa
