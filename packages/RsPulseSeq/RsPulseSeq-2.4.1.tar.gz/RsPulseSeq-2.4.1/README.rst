==================================
 RsPulseSeq
==================================

.. image:: https://img.shields.io/pypi/v/RsPulseSeq.svg
   :target: https://pypi.org/project/ RsPulseSeq/

.. image:: https://readthedocs.org/projects/sphinx/badge/?version=master
   :target: https://RsPulseSeq.readthedocs.io/

.. image:: https://img.shields.io/pypi/l/RsPulseSeq.svg
   :target: https://pypi.python.org/pypi/RsPulseSeq/

.. image:: https://img.shields.io/pypi/pyversions/pybadges.svg
   :target: https://img.shields.io/pypi/pyversions/pybadges.svg

.. image:: https://img.shields.io/pypi/dm/RsPulseSeq.svg
   :target: https://pypi.python.org/pypi/RsPulseSeq/

Rohde & Schwarz Pulse Sequencer radar simulation software RsPulseSeq instrument driver.

Basic Hello-World code:

.. code-block:: python

    from RsPulseSeq import *

    instr = RsPulseSeq('TCPIP::192.168.56.101::5025::SOCKET', reset=True)
    idn = instr.query_str('*IDN?')
    print('Hello, I am: ' + idn)

Check out the full documentation on `ReadTheDocs <https://RsPulseSeq.readthedocs.io/>`_.

Supported instruments: PulseSequencer

The package is hosted here: https://pypi.org/project/RsPulseSeq/

Documentation: https://RsPulseSeq.readthedocs.io/

Examples: https://github.com/Rohde-Schwarz/Examples/


Version history:
----------------

    Latest release notes summary: Included all three variants - RF, Digital, DFS

    Version 2.4.1.24
        - Included all three variants - RF, Digital, DFS

    Version 2.4.0.21
        - First release for FW 2.4
