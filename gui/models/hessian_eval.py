import numpy as np


def hesscorrgauss(x: np.ndarray, dmodel) -> np.ndarray:
    """Computation of Hessian matrix at current point x for a single output
    with Constant (regpoly0) and Linear (regpoly1) regression model, and Gauss
    (corrgauss) correlation model ONLY.

    Parameters
    ----------
    x: np.ndarray
        Trial design site.
    dmodel: Dace
        Dace model object containing the trained data.

    Returns
    -------
    h: np.ndarray
        Hessian evaluated at `x`. The order of columns/rows is the same as `x`.
    """

    if isinstance(dmodel, dict):
        # older version of pydace
        S = dmodel['S']
        Ssc = dmodel['Ssc']
        gamma = dmodel['gamma']
        # FIXME: apply flatten on newer version of pydace, maybe this is what
        # is causing hessian instability
        theta = dmodel['theta'].flatten()
        Ysc = dmodel['Ysc']
    else:
        S = dmodel.S
        Ssc = dmodel._Ssc
        gamma = dmodel._fitpar['gamma']
        theta = dmodel.theta.flatten()
        Ysc = dmodel._Ysc

    m, n = S.shape
    x = x.flatten()  # always work with 1D arrays
    if x.size != n:
        raise ValueError('x does not have the same dimension as S')

    x = (x - Ssc[0, :]) / Ssc[1, :]  # scale the input
    d = S - np.tile(x, (m, 1))

    gammaR = np.zeros((m,))

    for i in range(m):
        gammaR[i] = gamma[0, i] * \
            np.exp(-np.sum(theta * (d[i, :] ** 2)))

    # scaled hessian calculation
    h = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):
            aux = 0
            if i == j:
                for k in range(m):
                    aux += 2 * theta[i] * gammaR[k] * \
                        (-1 + 2 * theta[j] * d[k, i] * d[k, j])
            else:
                for k in range(m):
                    aux += 2 * theta[i] * gammaR[k] * \
                        (2 * theta[j] * d[k, i] * d[k, j])

            h[i, j] = aux
            h[j, i] = h[i, j]

    # unscaled hessian
    for i in range(n):
        for j in range(i, n):
            # change from index to 0 in Ysc (single output/univariate kriging)
            h[i, j] = Ysc[1, 0] / (Ssc[1, i] * Ssc[1, j]) * h[i, j]
            h[j, i] = h[i, j]

    return h
