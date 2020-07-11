***********************************
Propene/Propane Distillation Column
***********************************

.. figure:: ../images/c3splitterflowsheet.svg
   :align: center

   Flowsheet of the propene distillation column.

Placeholder text...

Dynamic simulations
===================

The best control structure that uses a linear combination of 3 measurements 
is chosen to evaluate the dynamic performance of this more complex control 
configuration for the C3-Splitter case study, where

.. math::

   Cv_1 = 0.00129t_{132} + 0.00126t_{133} + 0.00152vf

.. math::

   Cv_2 = 0.69671t_{132} + 0.69489t_{133} + 0.17807vf

The following plots clearly show that this choice is capable of dealing with  
disturbances in the composition of propene in the feed and total flow rate, 
while at the same time indirect controlling the primary variables. PI 
controllers tuned with the IMC rules and a process flowsheet depicting the 
control configuration in place is provided in :numref:`c3controlflowsheet`.

.. figure:: ../images/c3splitter_control_structure.svg
   :name: c3controlflowsheet
   :align: center

   Control structure tested.

.. plot:: images/pyplots/c3feedplus5.py
   :align: center

.. plot:: images/pyplots/c3feedminus5.py
   :align: center

.. plot:: images/pyplots/c3feedcompplus25.py
   :align: center

.. plot:: images/pyplots/c3feedcompminus25.py
   :align: center

.. plot:: images/pyplots/c3feedvfracplus10.py
   :align: center