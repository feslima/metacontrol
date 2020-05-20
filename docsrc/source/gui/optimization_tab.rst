**************************************************
The "Optimization" tab
**************************************************

This tab allows you to optimize the metamodel objective function, subject to the 
constraints that you have created (also metamodels). In addition, the bounds of the Manipulated Variables (MVs)
that you defined at the "Sampling" tab are automatically incorporated to the optimization problem as box constraints.

You can also:

* Modify the NLP (IpOpt) solver parameters
* Modifiy the infill criteria algorithm parameters, implemented in *Metacontrol* to refine your
  kriging response
* Inspect each iteration of the infill criteria algorithm in real time
* At the end of the run, see your results in a concise panel.

Here is an overview of this tab:

.. figure:: ../images/otm_main.png
   :align: center

   *Metacontrol* "Optimization" tab.

There are five main panels on this tab:

* Adaptive sampling setup *panel*
* NLP solvers options *panel*
* Perform optimization *panel*
* Control *panel*
* Results *panel*

Adaptive sampling setup *panel*
===============================

On this panel you will setup the main parameters for the Adaptive Sampling (infill criteria) algorithm.

.. figure:: ../images/adaptive_sampling.png
   :align: center

   Configuring adaptive sampling algorithm.

You can setup values for:

* *First* and *Second* contraction factors
* *Maximum* contraction tolerance
* Feasibility constraint tolerance
* Penalty factor for the objective function 
* Refinement tolerance
* Termination tolerance
* Maximum function evaluations
* The kriging regression model used in the adaptive sampling algorithm

.. IMPORTANT::
    For a explanation on how each parameters affects the optimization run, refer to our theoretical
    backgrounds section.


NLP solvers options *panel*
============================

You can select the NLP solver and configuring its parameters at this section. Currently, we support IpOpt inside
*Metacontrol* natively.

.. figure:: ../images/nlp_solvers.png
   :align: center

   Configuring NLP Solvers Parameters.



Perform optimization *panel*
============================

At this panel you can start your optimization run, or abort it at any moment.

.. figure:: ../images/perform_optimization.png
   :align: center

   Start/abort optimization run.

Performing an optimization run
-------------------------------

After configuring the adpative sampling and NLP parameters, you can click on "Start" under the
"Perform optimization" *panel* in order to begin the metamodel optimization. You can see at the Control
panel the iterations in real time, and each step performed by the algorithm.

Control *panel*
================

This is how the control *panel* looks like during an optimization run in *Metacontrol*:


.. figure:: ../images/opt_control_panel.png
   :align: center

   Control *panel* output.

The control panel shows (being updated in real time) the operations performed by the adaptive sampling algorithm, the decision variables values (MVs) at each
iteration, the actual and predicted objective function values, and the largest infeasiblity (constraint) violation for that iteration.
At the end of the optimization run, *Metacontrol* will inform you how many points are within the trust-region.

.. IMPORTANT::
    To understand how the algorithm works, refer to our theoretical backgrounds section.


Results *panel*
================

The results *panel* gives a summary of the results of your optimization problem, such as

* Final decision variables values
* Constraint expressions values
* Objective function value

.. figure:: ../images/opt_results.png
   :align: center

   Results *panel* , a summary of your optimization run.

Interpreting constraints results
---------------------------------

As stated before at the previous section, the constraints are written in *Metacontrol* in the form:

.. math:: 
    g(x) \leq 0

Therefore, if a constraint has, after the optimization run, a negative value, it indicates that this constraint
is **inactive**. On the other hand, constraints values equals 0 indicate that for the problem created, this constraint
is active. This information is important because Active-Constraint Control is a mandatory step in Self-Optimizing control
methodology.

In the example above, all nonlinear constraints were inactive. Three decision variables (MVs), on the other hand, were active
at their lower bounds (*mcct*, *f1t* and *f2t*).
