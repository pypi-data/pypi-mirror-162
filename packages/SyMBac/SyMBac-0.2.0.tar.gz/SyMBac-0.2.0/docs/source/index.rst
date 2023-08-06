SyMBac Documentation
====================

.. image:: https://readthedocs.org/projects/symbac/badge/?version=latest
   :target: https://symbac.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://pepy.tech/badge/symbac
   :target: https://pepy.tech/project/symbac

.. image:: https://badge.fury.io/py/symbac.svg
   :target: https://badge.fury.io/py/symbac

SyMBac (Synthetic Micrographs of Bacteria) is a tool to generate synthetic phase contrast or fluorescence images of bacteria. Currently the tool only supports bacteria growing in the mother machine, however support for bacteria growing in monolayers (and maybe even biofilms!) is coming. 

Read the preprint_, SyMBac: Synthetic Micrographs for Accurate Segmentation of Bacterial Cells using Deep Neural Networks, Georgeos Hardo, Maximillian Noka, Somenath Bakshi

.. note::

   This project is under active development. Please report issues on GitHub, or if you want specific usage help, please email_ me.


Contents
--------


.. toctree::
   :caption: Introduction
   :maxdepth: 3

   intro
   installation
   faqs

.. toctree:: 
   :caption: Detailed guide: Mother Machine
   :maxdepth: 3

   cell_growth_simulation
   scene_generation

.. toctree:: 
   :caption: Detailed guide: Agar Pad
   :maxdepth: 3



.. toctree::
   :caption: Examples
   :maxdepth: 3

   Drawing_Phase_Contrast_100x_oil

.. toctree:: 
   :caption: API reference
   :maxdepth: 3

   symbac_cell_geometry
   symbac_general_drawing
   symbac_misc
   symbac_phase_contrast_drawing
   symbac_PSF

.. _preprint: https://www.biorxiv.org/content/10.1101/2021.07.21.453284v4

.. _email: gh464@cam.ac.uk

.. _DeLTA: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007673

.. _Omnipose: https://www.biorxiv.org/content/10.1101/2021.11.03.467199v4
