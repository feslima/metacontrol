************
Introduction
************

What is Metacontrol ?
================================================

The primary objective of the *Metacontrol* methodology is to facilitate the 
implementation of the Self-Optimizing Control (SOC) concept in industrial
processes via software analysis, in a comprehensive user interface.

The SOC concept is used to guide a decision on how to design the control 
structure of a given process. 


By definition from the main author of the methodology, Dr. Sigurd Skogestad
from NTNU:

"**Self-optimizing control is when one can achieve an acceptable loss with 
constant setpoint values for the controlled variables without the need to re-optimize 
when disturbances occur.**"

.. figure:: /images/plot_soc.svg
   :align: center

   Self-Optimizing Control fundamental concept: The pursue of a control
   structure based on constant setpoint policy, capable of minimizing the loss to an acceptable
   magnitude, when compared with the reoptimized process every time that a disturbance occur (Real Time
   Optimization).


The self-optimizing control structure selection problem has a combinatorial nature: Generally in an industrial process,
there are dozens (even thousands!) of variables, and a set of available degrees of freedom that can be consumed
by a subset of the possible candidate controlled variables. There are mainly two ways to solve this problem:

* **"Brute-force" Approach**: 
    Each possible control structure is evaluated, one at a time. 
    Depending on the number of the degrees of freedom and available measurements, 
    that can take literally, **forever**.

* **Local (linear) methods**: 
    Based on quadratic approximation of the objective function using 
    Taylor series expansions, Local methods were developed by Dr. Sigurd Skogestad and his 
    collaborators to quickly "pre-screen" the most promising subsets of controlled variables. 
    *Metacontrol* is based on these mathematical formulations, with a neat User Interface.




In order to use the Local methods, it is necessary to obtain high-order data with respect to the
process gradients and the objective function hessians. In order to do this, *Metacontrol* uses
powerful machine learning formulations (Kriging Interpolators) to obtain such data in with
robustness.



Last but not least, other decisions such as which type of 
controllers to use or how to tune them is a responsibility of *classical 
control design*, whose concepts are not implemented (yet) in this software.



.. IMPORTANT::
    The basic idea behind *Metacontrol* is to tell you **what** control 
    structure you should implement, **not how** you should implement.

Nonetheless, *Metacontrol* is a congregation of methodologies such as 
`Surrogate modeling <https://en.wikipedia.org/wiki/Surrogate_model>`_ via
`Kriging metamodels <https://en.wikipedia.org/wiki/Kriging>`_,
`Black-box process optimization <http://www.ressources-actuarielles.net/EXT/ISFA/1226.nsf/9c8e3fd4d8874d60c1257052003eced6/e7dc33e4da12c5a9c12576d8002e442b/$FILE/Jones01.pdf>`_
and `SOC <https://folk.ntnu.no/skoge/research/research-selfopt.html>`_, In order to determine
process optimal operating point, high-order data obtainment to use SOC mathematical formulations and
consequently, generating SOC-based control structures. 
All of that within a comprehensive User Interface,
allowing the control structure designer/engineer/scientist (hey, that's you) to keep his/hers focus only on
synthesizing the control structure, rather than wasting hours "jumping" between several software environments, such as: Process simulators (Aspen Plus) and
numerical packages (MATLAB, Python, Microsoft Excel, etc.). This tool is made by Engineers that struggled with this (us),
in order to try to solve such struggle for the scientific community.

Installation
============

Currently, there are two ways to install the software: via binaries or 
source code.

**Prerequisites**:

    #. Windows OS;
    #. `AspenTech Aspen Plus <https://www.aspentech.com/en/products/engineering/aspen-plus>`_ installed;

Installing from binaries  (.exe)
--------------------------------

This is the most straightforward way to install *Metacontrol*. You just need to 
download and install the desired version (generally, our most recent and stable version) from the repository 
`releases page <https://github.com/feslima/metacontrol/releases>`_.

This is the recommended option for most engineers and scientists that just want to study SOC-Based Control Structure selection and are
not interested in programming details.
You will only install our software and will be good to go.



Installing from source
----------------------

*Metacontrol* as stated before, is fully open-source. Want to inspect or change our code?
Just follow the steps below!

**Additional prerequisites**:

    * A conda installation from either `Anaconda <https://www.anaconda.com/>`_ or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_;

**Steps**:

#. Create the virtual environment.

    You will need to create a conda environment exclusively for 
    *Metacontrol* and install the `Python interpreter <https://www.python.org/>`_ 
    via the following conda prompt command::

        conda create -n your_env_name -c conda-forge python

    The argument ``your_env_name`` can be changed to whichever valid name you like.
    We suggest to keep it simple to remember (simply calling ``metacontrol`` or 
    ``mtc`` will suffice), since you will need it activated whenever you run 
    the *Metacontrol* application.

#. Then activate the environment via:

    ::

        conda activate your_env_name

#. Install the optimization package.

    Now you will need to install the `Python IpOpt optimization package <https://github.com/matthias-k/cyipopt>`_ 
    required. This step is crucial, so we recommend you follow the package 
    `installation instructions <https://github.com/matthias-k/cyipopt#from-source-on-windows>`_ 
    accordingly.

#. Then you will need to install the base packages via the commands:

    .. code-block:: sh

        conda install -c conda-forge pywin32 pandas sklearn simplejson matplotlib scipy
        
        pip install py-expression-eval

        conda install -c felipes21 pydace surropt pysoc

#. Download the *Metacontrol* source code.

    From the `repository <https://github.com/feslima/metacontrol>`_ 
    and unzip it to your folder of preference.

#. Run the application:

    You will need to have a conda prompt with the environment you created in the 
    previous steps activated. Then you just type the command::

        python path/to/mainwindow.py

    The argument ``path/to/`` is just the path to folder you unzipped. Your can 
    either change the current directory via the ``cd`` command and running 
    ``python mainwindow.py``, or type the full path as mentioned above.