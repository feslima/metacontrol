************
Introduction
************

What Metacontrol is capable of and what it isn't
================================================

The primary objective of the *Metacontrol* methodology is to facilitate the 
implementation of the Self-Optimizing Control (SOC) concept in industrial
processes via software analysis.

The SOC concept is used to guide a decision on how to design the control 
structure of a given process. Other decisions such as which type of 
controllers to use or how to tune them is a responsibility of classical 
control design whose concepts are not implemented (yet) in this software.

.. IMPORTANT::
    The basic idea behind *Metacontrol* is to tell you **what** control 
    structure you should implement, **not how** you should implement.

Nonetheless, *Metacontrol* is a congregation of methodologies such as 
`Surrogate modeling <https://en.wikipedia.org/wiki/Surrogate_model>`_ via
`Kriging metamodels <https://en.wikipedia.org/wiki/Kriging>`_,
`Black-box process optimization <http://www.ressources-actuarielles.net/EXT/ISFA/1226.nsf/9c8e3fd4d8874d60c1257052003eced6/e7dc33e4da12c5a9c12576d8002e442b/$FILE/Jones01.pdf>`_
and `SOC <https://folk.ntnu.no/skoge/research/research-selfopt.html>`_.

Installation
============

Currently, there are two ways to install the software: via binaries or 
source code.

**Prerequisites**:

    #. Windows OS;
    #. `AspenTech Aspen Plus <https://www.aspentech.com/en/products/engineering/aspen-plus>`_ installed;

Installing from binaries
------------------------

This is the most straightforward way to install *Metacontrol*. You just need to 
download and install the desired version from the repository 
`releases page <https://github.com/feslima/metacontrol/releases>`_.

Installing from source
----------------------

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