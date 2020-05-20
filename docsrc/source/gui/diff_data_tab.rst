**************************************************
The "Differential Data" tab
**************************************************

At this tab you will extract the high-order data (Gradients and Hessians)
that are necessary in order to calculate the self-optimizing control structures using
the exact local method from :cite:`alstad09`. 

The high-order data is calculated with
analytical expressions derived by :cite:`DACE` and :cite:`alves2018`, using the kriging 
metamodel built for the reduced space problem.


The aforementioned procedure is encapsulated in this tab. You will be able to:

* Generate the gradients and hessians, and inspect them.
* Remove any CV candidate from the list of candidates if you want.

Here is an overview of this tab, before you start using it:






Bibliography
=============
.. bibliography:: ../mybibfile.bib