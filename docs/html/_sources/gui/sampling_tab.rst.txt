**************************************************
The "Sampling" tab
**************************************************

At this tab you will use the simulation provided on the last step to
perform a Design of Experiments (DOE). You will be able to:

* Define the lower and upper bounds for your manipulated variables, that will
  be used as the limits of the sampling and as box constraints of the optimization 
  problem
* Define the number of sampled cases
* Inspect the results of the sampling, for each variable that you selected on the last
  step
* Check convergence status of each case


Here is an overview of this tab:

.. figure:: ../images/sampling_tab.png
   :align: center

   *Metacontrol* "Sampling" tab.


There are three main panels on this tab:

* Bounds definition *panel*
* Sampling assistant *panel*
* DOE Results *panel*


Bounds definition *panel*
==========================

This is the panel that you will define the upper and lower bounds of
the Manipulated Variables that you chose. These limits will be used to sample
your data, if you choose to use your Aspen Plus model in order to do so. In addition,
these limits will be automatically used as box constraints at the optimization step.
Note that the aliases that you chose for you Manipulated Variables are neatly shown
here.

.. figure:: ../images/bounds_definition.png
   :align: center

   Bounds definition panel.

Inserting the lower and upper bounds for your MVs
--------------------------------------------------

That's pretty straightforward. Simply click on each variable "Lower Bound" and "Upper Bound"
field, and type it:

.. figure:: ../images/input_bounds.png
   :align: center

   Insert bounds for your MVs.

Sampling Assistant *panel*
==========================

This panel defines how are you going to supply the DOE data to metacontrol: Using your simulation file (recommended) or
loading an *.CSV file (this is a auxiliary feature). For the first case, you are going to use the Sample Assistant from *Metacontrol*:

Using the Sampling Assistant to sample data from Aspen Plus
------------------------------------------------------------

Click on "Open Sampling Assistant":

.. figure:: ../images/sampling_assistant_select.png
   :align: center

   Selecting the Sampling Assistant.

The Sampling Assistant Screen will be revealed:

.. figure:: ../images/sampling_assistant_main.png
   :align: center

   Selecting the Sampling Assistant.

.. IMPORTANT::
   Currently, *Latin Hypercube Sampling* (LHS) is the main sampling technique used in *Metacontrol*.
   Check our publications for a justification for its usage.

Clicking on the "Gear" Icon at the "Select a Sampling Method" panel, you will be able to define the number
of desired cases and how many iterations the LHS routine will perform in order to improve the sampling. Generally, 
a value of 5 is enough. In this case, we are going to run 80 cases. In addition, you can opt to include the
vertices of the hypercube of your design.

.. figure:: ../images/sampling_no_of_cases.png
   :align: center

   Defining the number of cases.

Clicking on "ok" will bring you to the previous screen, and you can generate the input data by the LHS method:

.. figure:: ../images/sampling_lhs_gen.png
   :align: center

   Generating LHS Input data.

Notice that now under the "Sampler Display" panel, the LHS Input data is show (Here, intentionally highlighted in blue):

.. figure:: ../images/sampling_lhs_ready.png
   :align: center

   LHS Input data.

The "Sample Data" button now is available. Push it to start running your cases. 


.. figure:: ../images/sampling_lhs_run.png
   :align: center

   Running you Design Of Experiments (DOE).


At each case, *Metacontrol*
communicates with the Aspen Plus Engine, and collects the results automatically and in real time. You can literally see the
sampling process in front of you, with the "Sampler Display" panel being updated as the cases run.

.. figure:: ../images/sampling_running.png
   :align: center

   Running you Design Of Experiments (DOE): Notice that you
   are able to abort this at any moment, simply hitting the "Abort"
   button at the left corner.

DOE Results *panel*
==========================

After the sampling process is complete, you can click on "Done", to save your progress and your sampled data.
If you click in "Cancel", the sampling is discarded and if you click in "Export as CSV", you will be able to
save your design of experiments as a .csv file at your computer if you want.

After clicking in "Done", you will be sent to the Sampling tab and you will 
notice that your data is displayed under the "DOE Results" panel. With this, you are able
to go to the next tab: Metamodel.

.. figure:: ../images/sampling_end.png
   :align: center

   Your Design Of Experiments (DOE) with all data generated, after consulting Aspen Plus.