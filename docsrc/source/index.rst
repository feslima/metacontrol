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


.. _our_papers:

Our papers
-----------
Please, cite the related papers:

#. `Metamodel-Based Numerical Techniques for Self-Optimizing Control <https://pubs.acs.org/doi/10.1021/acs.iecr.8b04337>`_;
   
   **BibTeX Entry:**

   .. code-block:: none

      @article{alves2018metamodel,
         title={Metamodel-Based Numerical Techniques for Self-Optimizing Control},
         author={Alves, Victor MC and Lima, Felipe S and Silva, Sidinei K and Araujo, Antonio CB},
         journal={Industrial \& Engineering Chemistry Research},
         volume={57},
         number={49},
         pages={16817--16840},
         year={2018},
         publisher={ACS Publications}
         }

#. `Metacontrol: A Python based application for self-optimizing control using metamodels <https://www.sciencedirect.com/science/article/abs/pii/S0098135420303355>`_;

   **BibTeX Entry:**

   .. code-block:: none

      @article{lima2020metacontrol,
         title={Metacontrol: A Python based application for self-optimizing control using metamodels},
         author={Lima, Felipe Souza and Alves, Victor Manuel Cunha and de Araujo, Antonio Carlos Brandao},
         journal={Computers \& Chemical Engineering},
         volume = {140},
         pages = {106979},
         year = {2020},
         issn = {0098-1354},
         doi = {https://doi.org/10.1016/j.compchemeng.2020.106979},
         url = {http://www.sciencedirect.com/science/article/pii/S0098135420303355},
         publisher={Elsevier}
         }


And become a watcher/stargazer on `GitHub <https://github.com/feslima/metacontrol>`_ to receive updates!


Features
==============

Open-Source
==============
*Metacontrol* is **open-source**, under the **GPL v3.0** license. We believe that open code just makes
scientific development clearer and generally better. Want to inspect our code? Maybe change it for your
specific desire? Have a suggestion? Go for it. Share with us!


Built in Python
================
The scientific world and data scientists are moving in a accelerated pace to Python programming language. *Metacontrol* was built from scratch using it. Using state-of-the-art packages
such as `Numpy <https://numpy.org/>`_, `Scipy <https://www.scipy.org/>`_, `pyQT <https://www.riverbankcomputing.com/software/pyqt/>`_, `pandas <https://pandas.pydata.org/>`_ and many others, a concise and standalone software is available. You will **not** need any other
software, apart from the process simulators (obviously), to run our application.

Support for Optimization using metamodels
==========================================

One crucial step of Self-Optimizing Control methodology is to optimize a process model. 
We use the the famous `IpOpt <https://github.com/coin-or/Ipopt>`_ Optimization package (using a `Python Interface <https://github.com/matthias-k/cyipopt>`_) in order to do it. Therefore, you can also use *Metacontrol*
to optimize processes that you modeled in Aspen Plus.

Usage of Kriging metamodels
============================
Kriging interpolators are widely used in the scientific community for prediction, optimization and data obtainment.
We use it to for optimization and high-order data obtainment purposes. It is proven to generate robust precitions and results.
For further details, check :ref:`our_papers`.


State-of-the-art Self-Optimizing Control techniques
====================================================

Standing on the shoulders of giants, *Metacontrol* uses the most recent formulations in the SOC area available that are capable of
quickly pre-screening the most promising candidate controlled variables from a given universe of possible combinations. This includes
the exact local Method with explicit solution from :cite:`alstad09` and even branch-and-bound 
algorithms :cite:`kariwala2009` under the hood.


Documentation Contents
==================================

.. toctree::
   :maxdepth: 2

   intro
   overview/mtc
   gui/gui_index.rst
   examples/tutorials
   theory/theory_index
   zbibliography



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
