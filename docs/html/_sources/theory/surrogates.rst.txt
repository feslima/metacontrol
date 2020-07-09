******************************
Surrogate modeling - Kriging
******************************

Metamodels are a way to represent the world in simpler terms. Think of them as 
a photograph, they do not capture the moment as whole but can represent it 
good enough. In this analogy, the moment is a complex process that it is too 
cumbersome to explain it completely in mathematical terms, and metamodels, as 
photographs, may serve the purpose of capturing the core trends of this 
process without being too unwieldy and not losing too much information.

There is a family of metamodeling methodologies, ranging from a simple linear 
regression to complex neural networks. However, the surrogate methodology 
currently implemented in *Metacontrol* is the *Kriging*.

The simplest form to represent a real world process (:math:`y`) through a 
metamodel (:math:`\hat{y}`) and its error (:math:`\varepsilon`) is done 
through :eq:`surreq`.

.. math::
    :label: surreq
    
    y(x) = \hat{y}(x) + \varepsilon

The error (:math:`\varepsilon`) is associated with the unmodeled effects of 
the inputs (:math:`x`) and random noise (i.e. it cannot be explained in detail 
but cannot be ignored as well.). When using the *Kriging* methodology as 
metamodel, this error is assumed to be a probabilistic function of :math:`x`, or 
in other words, this error is assumed to be **not** independent and identically 
distributed. The specific probabilistic function is represented by a Gaussian 
distribution with mean (:math:`\mu`) zero and variance :math:`\sigma^2`.

As from :cite:`DACE`, a *Kriging* metamodel :math:`\hat{y}(x)`, of a 
rigorous model :math:`y(x)` of :math:`q` dimensions, is comprised 
of two parts: a polynomial regression (:math:`\mathcal{F}`) and departure 
function (:math:`z`) of stochastic nature:

.. math::
    \hat{y}_{l}(x)=\mathcal{F}\left(\beta_{:, l}, x\right)+z_{l}(x), 
    \quad l=1, \ldots, q

The regression model, considered as a linear combination of (:math:`t`) 
functions (:math:`f_{j}: \mathbb{R}^{n} \rightarrow \mathbb{R}`), as defined 
in :eq:`kr2`.

.. math::
    :label: kr2

	\mathcal{F}\left(\beta_{:, l}, x\right) \equiv f(x)^{T} \beta_{:, l}

The most common choices for :math:`f(x)` are polynomials with orders ranging 
from zero (constant) to two (quadratic). It is assumed that :math:`z` has 
mean zero, and the covariance between to given points, arbitrarily named 
:math:`w` and :math:`x` for instance, is defined by :eq:`kr3`:

.. math::
    :label: kr3

    \operatorname{Cov}\left[z_{l}(w), z_{l}(x)\right]=\sigma_{l}^{2} 
    \mathcal{R}\left(\theta_{l}, w, x\right), \quad l=1, \ldots, q

With :math:`\sigma_{l}^{2}` being the process variance for the *lth* response 
component, and :math:`\mathcal{R}(\theta, w, x)` defined as the correlation 
model. In *Metacontrol*, the correlation model used is described by :eq:`kr4`.

.. math::
    :label: kr4

    \mathcal{R}\left(\theta_{l}, w, x\right)=\exp \left(-\sum_{i=1}^{m} 
    \theta_{l}\left(w-x_{i}\right)^{p}\right), \quad\left(\theta_{l} \geq 0, 
    p_{l} \in[0,2]\right)

The hyperparameters :math:`\theta` are degrees of freedom available for 
optimization purposes, seeking the improvement of the metamodel fitness. In 
:cite:`DACE`, the optimal set of hyperparameters :math:`\theta^*` corresponds 
to the maximum likelihood estimation. Assuming a Gaussian process, the optimal 
values of the hyperparameters are the ones that minimize :eq:`kr5`:

.. math::
    :label: kr5

    \min _{\theta}\left\{\psi(\theta) \equiv|R|^{\frac{1}{m}} 
    \sigma^{2}\right\}

Where :math:`|R|` is the determinant of the correlation matrix. The internal 
optimizer used in *DACE* toolbox corresponds to a modified version of 
the *Hooke & Jeeves* method, as showed by :cite:`dacereport`.

As stated before, high-order data obtainment it is an obligatory step in the 
proposed methodology implemented in \mtc. Fortunately, :cite:`DACE` 
also derived expressions for Jacobian (:math:`\hat{y}^{\prime}(x)`) 
evaluation of a *Kriging* prediction, given in :eq:`kr6`:

.. math::
    :label: kr6

	\hat{y}^{\prime}(x)=J_{f}(x)^{T} \beta^{*}+J_{r}(x)^{T} \gamma^{*}

The expression for Hessian evaluation was derived by :cite:`alves2018` 
(full demonstration in appendix A of their work), and it is depicted in 
:eq:`kr7`:

.. math::
    :label: kr7

	\hat{y}^{\prime \prime}(x)=H_{f}(x) \beta^{*}+H_{r}(x) \gamma^{*}

Equations :eq:`kr6` and :eq:`kr7` are one of the staples of the *Metacontrol* .
