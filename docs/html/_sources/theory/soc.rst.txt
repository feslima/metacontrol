**********************************************
The Exact Local Method with Explicit Solution
**********************************************

Every  industrial process is under limitations ranging from design/safety (e.g. 
temperature or pressure which an equipment can operate, etc.), environmental 
(e.g. pollutant emissions), to quality specifications (e.g. product purity), 
and economic viability. More often than not, these constraints are applied all 
at once and can be conflicting. Therefore, it is mandatory to operate such 
processes optimally (or, at least, close to its optimal point) in order to 
attain maximum profits or keep expenses at minimum while still obeying these 
specifications.

One way to achieve this is through the application of plantwide control 
methodologies. In particular, Self-Optimizing Control (SOC) 
:cite:`morari1980,skoge00,alstad09`, is a practical way to design a control 
structure of a process following a criterion (for instance: economic, 
environmental or performance) considering a constant set-point policy 
:cite:`alves2018`. The SOC methodology is advantageous in this scenario 
because there is no need to reoptimize the process every time that a 
disturbance occurs.

However, the review presented here contains merely the paramount elements 
needed to understand the main concepts and expressions that translate the 
ideas behind the SOC methodology. If the reader needs a more detailed 
explanation can be found in 
:cite:`skoge00,halvorsen03,hori05,hori07,alstad09,alves2018,kariwala08,kariwala2009,umar12`.

From :cite:`skoge04`:

    "Self-optimizing control is when one can achieve an acceptable loss with 
    constant setpoint values for the controlled variables without the need to 
    reoptimize when disturbances occur."

It is assumed the process objective function, assumed scalar, is influenced by 
its steady-state operation. Therefore, the optimization problem described in 
:eq:`optproblem` is formed, with :math:`J` being the cost function, 
:math:`u_{0}` being the degrees of freedom available, :math:`x` and 
:math:`d` representing the states and the disturbances of the system, 
respectively.

.. math::
    :label: optproblem

    \begin{aligned}
	& \underset{u_{0}}{\text{minimize}}
	& & J_{0}\left(x, u_{0}, d\right) \\
	& \text{subject to}
	& & g_{1}\left(x, u_{0}, d\right)=0 \\
	& & & g_{2}\left(x, u_{0}, d\right) \leq 0
	\end{aligned}

Regarding the disturbances, these can be: change in feed conditions, prices 
of the products and raw materials, specifications (constraints) and/or changes 
in the model. Using NLP solvers, the objective function can be optimized 
considering the expected disturbances and implementation errors.

Since the whole technology considers near-optimal operation, as a result of 
keeping constant setpoints (differently from RTO, for instance), there will 
always exist a (positive) loss, given by :eq:`generalloss`:

.. math::
    :label: generalloss

	L=J_{0}(d, n)-J_{opt}(d)

*Metacontrol* focus on the first four steps of the SOC technology, named by 
:cite:`skoge00` as "top-down" analysis. In these steps, the variable 
selection seeking the usage of the steady-state degrees of freedom 
is the main problem to be addressed with the systematic procedure proposed. It 
is possible to search for a SOC structure basically using two methods:

#. Brute-force approach:
    Manually testing each CV candidate, reoptimizing the process for 
    different disturbances' scenarios, and choosing the structure that yields 
    the lowest (worst-case or average-case) loss;

#. Local approximations:
    Using local methods based on second-order Taylor series expansion of 
    the objective function, that are capable of easily and quickly 
    "pre-screening" the most promising CV candidates;

The manual nature of the brute-force approach and the possibility of creating 
an automated framework using local approximations motivated the creation 
of *Metacontrol* itself. However, the current version of the software only 
implements the second method.

Therefore, a linear model with respect to the plant measurements (:math:`y`) 
can be represented as :eq:`linear1`.

.. math::
    :label: linear1

	\Delta y=G^{y} \Delta u+G_{d}^{y} \Delta d

with:

.. math::
    \begin{array}{l}
		{\Delta y=y-y^{*}} \\
		{\Delta u=u-u^{*}} \\
		{\Delta d=d-d^{*}}
    \end{array}

Where :math:`u` are the manipulated variables (MV), :math:`G^{y}` and 
:math:`G^{y}_{d}` are the gain matrices with respect to the measurements 
and disturbances, respectively. Regarding the candidate variables (CV), 
linearization will give :eq:`cvlinear`:

.. math::
    :label: cvlinear

	\Delta c=H \Delta y=G \Delta u+G_{d} \Delta d

With

.. math::
    \begin{array}{l}
        {G=HG^{y}} \\
        {G_{d}=H G_{d}^{y}}
    \end{array}

Where :math:`H` is a linear combination matrix of the CVs.

Linearizing the loss function :eq:`generalloss` results in :eq:`linearloss`:

.. math::
    :label: linearloss

    \begin{aligned}
		L &=J(u, d)-J_{o p t}(d)=\frac{1}{2}\|z\|_{2}^{2} \\
		z=& J_{u u}^{\frac{1}{2}}\left(u-u_{o p t}\right)=J_{u u}^{\frac{1}{2}} G^{-1}\left(c-c_{o p t}\right)
	\end{aligned}

where :math:`J_{uu}` being the Hessian of cost function with respect to the 
manipulated variables :math:`\left(\frac{\partial^{2} J}{\partial^{2} u}\right)` 
and :math:`J_{ud}` being the Hessian of cost function with respect to the 
disturbance variables 
:math:`\left(\frac{\partial^{2} J}{\partial u\partial d}\right)`.

Later :cite:`halvorsen03`, developing the exact local method, showed that 
the loss function can be rewritten as in :eq:`lossexact`

.. math::
    :label: lossexact

	z=J_{u u}^{\frac{1}{2}}\left[\left(J_{u u}^{-1} J_{u d}-G^{-1} G_{d}\right) \Delta d+G^{-1} n\right]


If one assumes that :math:`W_d` is a (diagonal) magnitude matrix that 
considers the disturbances and :math:`W_{n}^y` the magnitude matrix that 
takes into account the measurement error, and considering that both are 
2-norm-bounded (:cite:`halvorsen03` and :cite:`alstad09` contains a discussion 
and justification for using 2-norm), :eq:`2norm1` to :eq:`2norm3` can be 
defined to scale the system:

.. math::
    :label: 2norm1

	d-d^{*}=W_{d} d^{\prime}

.. math::
    :label: 2norm2

	n=H W_{n}^{y} n^{y^{\prime}}=W_{n} n^{y^{\prime}}

Where :math:`n^{y^{\prime}}` being the implementation error with respect to the 
measurements

.. math::
    :label: 2norm3

	\left\|\left(\begin{array}{l}
		{d^{\prime}} \\
		{n^{y^{\prime}}}
    \end{array}\right)\right\|_{2} \leq 1

The loss function from :eq:`linearloss` can be also written in a more 
appropriate way considering the definition of :cite:`alstad09` of the 
uncertainty variables regarding the contribution of the disturbances and 
measurement error on the incurred loss, :eq:`linearM` and considering 
the scaled system from :eq:`2norm1` to :eq:`2norm3`

.. math::
    :label: linearM

	M \triangleq\left[M_{d} \quad M_{n}^{y}\right]

where:

.. math::
    \begin{aligned}
		&M_{d}=-J_{u u}^{1 / 2}\left(H G^{y}\right)^{-1} H F W_{d}\\
		&M_{n^{y}}=-J_{u u}^{1 / 2}\left(H G^{y}\right)^{-1} H W_{n^{v}}
    \end{aligned}

with :math:`F` being the optimal measurement sensitivity matrix with respect to 
the disturbances.

Finally, if one uses all the definitions described so far, the worst-case loss 
for the effect of the disturbances and measurement error is given by 
:eq:`lossM`:

.. math::
    :label: lossM

	L_{worst-case} = \max _{\left\|\left(\begin{array}{l}
		{d^{\prime}} \\
		{n^{y^{\prime}}}
		\end{array}\right)\right\|_{2} \leq 1}=\frac{\bar{\sigma}(M)^{2}}{2}

:eq:`lossM` shows that in order to minimize the worst-case loss, it is 
necessary to minimize :math:`\bar{\sigma}(M)`, :eq:`argminH`:

.. math::
    :label: argminH

	H=\arg \min _{H} \bar{\sigma}(M)

This optimization problem was initially solved using a numerical search, as 
proposed by :cite:`halvorsen03`. Fortunately, :cite:`alstad09` 
derived an explicit solution that gives the optimal linear combination of 
measurements coefficient matrix (H) that minimize the worst-case loss that 
exists due to the effect of the disturbances and measurement errors, in 
:eq:`Hexact`:

.. math::
    :label: Hexact

	H^{T}=\left(\tilde{F} \tilde{F}^{T}\right)^{-1} G^{y}\left(G^{y T}\left(\tilde{F} \tilde{F}^{T}\right)^{-1} G^{y}\right)^{-1} J_{u u}^{1 / 2}

where

.. math::
	\tilde{F}=\left[F W_{d} W_{n}^{y}\right]

Assuming that :math:`\tilde{F} \tilde{F}^{T}` is full rank.

:eq:`Hexact` has three interesting properties proved by :cite:`alstad09`: 

#. It applies to any number of measurements (:math:`n_{y}`).
#. The solution for :math:`H` was proved to minimize not only the 
   worst-case, but also the average-case loss. Therefore, if one uses 
   :eq:`Hexact` seeking the determination of a control structure that 
   minimizes the loss at the worst-case scenario, he is also minimizing the 
   loss for the average-case scenario. This was called as a "super-optimality" 
   by :cite:`alstad09`.
#. The solution proposed minimizes the *combined* effect of the 
   disturbances and the measurement errors, simultaneously.

Therefore, the usage of the explicit solution will give both the minimized worst 
and average case losses using a single evaluation, and will also consider the 
combined effect of the disturbances and measurement errors of the problem. 
Therefore, this solution it is the default one used in *Metacontrol*.

Since :eq:`Hexact` also minimizes the worst-case loss, its evaluation 
was also considered inside *Metacontrol*: the user can inspect the expected 
average-case loss for each control structure that can exist in the 
combinatorial problem. The expression for the average-case loss is a result of 
the work of :cite:`kariwala08` and is described in :eq:`avgloss`:

.. math::
    :label: avgloss

	L_{\text {average}}=\frac{1}{6\left(n_{y}+n_{d}\right)}\left\|J_{u u}^{\frac{1}{2}}\left(H G^{y}\right)^{-1} H \widetilde{F}\right\|_{F}^{2}

Lastly, it was necessary to implement within *Metacontrol* a branch-and-bound 
algorithm capable of quickly searching the best control structures for each 
possible subset of a given process, using the incurred loss as metric. This was 
considered by the authors of :cite:`alves2018` as an obligatory feature, 
since when *Metacontrol* is being used, it was understood that the main 
idea was to, in a comprehensive software, the user operating it should be 
capable of inspecting the most promising control structures, and discarding 
the unnecessary evaluation of the unpromising structures (i.e.: With a high 
incurred loss - both average of worst-case scenario) to save time and effort. 
It is important to remember that there is an evident combinatorial problem 
that grows in an explosive fashion, as the number of the unconstrained 
degrees of freedom of the reduced space problem and the number of available 
measurements both increases. Without a search method that is capable of 
quickly discarding undesired solutions, the usability of *Metacontrol* would be 
seriously compromised. Luckily, there are several implementations of 
branch-and-bound algorithms tailored for SOC studies purposes, such as 
in :cite:`cao05,cao08,kariwala2009`.

From the aforementioned works, :cite:`kariwala2009` it is of particular 
interest: the monotonic criterion implemented consists of the exact local 
method from :cite:`halvorsen03` and derived explicitly by 
:cite:`alstad09`, which is used as the default methodology to pre-screen 
the most promising self-optimizing CV candidates in *Metacontrol*. Therefore, 
the usage of the proposed branch-and-bound algorithm by :cite:`kariwala2009` it 
is not only convenient, making the software more effective, but also keeps the 
"calculation engine" from *Metacontrol* using the same criterion. It would not 
make any sense, for instance, using a branch-and-bound algorithm that outputs the 
index of the most promising CVs using the maximum singular value rule from 
:cite:`skogebook` and use the CV index sequence from this algorithm 
to evaluate the worst-case loss. Fundamentally speaking, the orders of 
"best" control structures would not be the same, simply because the search 
method would be using an different criterion from the linear method 
implemented to evaluate the :math:`H` matrix.