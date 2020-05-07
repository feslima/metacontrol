.. Metacontrol documentation master file, created by
   sphinx-quickstart on Sat May  2 15:39:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Metacontrol: A metamodel based toolbox for self-optimizing control structure selection
======================================================================================

Metacontrol is a Python based software which assembles several methodologies 
into a single bundle so that a fast implementation of the Self-Optimizing 
Control (SOC) technique can be achieved.

How to cite us
==============

Please, cite the related paper:

.. code-block:: none

   place BibTeX entry here

And put a star on GitHub (Star GITHUB HERE)


Features
==============

Open-Source
==============
*Metacontrol* is *open-source*, under the MIT license. We believe that open code just makes
scientific development more clear and generally better. Want to inspect our code? Maybe change it for your
specific desire? Have a suggestion? Go for it. Share with us!


Built in Python
================
The scientific world and data scientists are moving in a accelerated pace to Python programming language. *Metacontrol* was built from scratch using it. Using state-of-the-art packages
such as *Numpy*, *Scipy*, *pyQT* and many others, a concise and standalone software is available. You will not need any other
software, apart from the process simulators (obviously), to run our application.

Support for Optimization using metamodels
==========================================

One crucial step of Self-Optimizing Control methodology is to optimize a process model. 
We use the the famous *IpOpt* Optimization package in order to do it. Therefore, you can also use *Metacontrol*
to optimize processes that you modelled in Aspen Plus.

Usage of Kriging metamodels
============================
Kriging interpolators are widely used in the scientific community for prediction, optimization and data obtainment.
We use it to for optimization and high-order obtainment purposes. It is proven to generate robust precitions and results.
For further details, check our papers.


State-of-the-art Self-Optimizing Control techniques
====================================================

Standing on the shoulders of giants, *Metacontrol* uses the most recent formulations in the SOC area available that are capable of
quickly pre-screening the most promising candidate controlled variables from a given universe of possible combinations. This includes
the exact local Method with explicit solution from Alstad et al. (2009) and even branch-and-bound algorithms by Cao et al. (2009) under the hood.


Documentation Contents
==================================

.. toctree::
   :maxdepth: 2

   intro
   overview/mtc
   theory/theory_index
   examples/tutorials



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
