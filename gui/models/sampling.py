from pydace.aux_functions import lhsdesign
import numpy as np


def lhs(n_samples: int, lb: list, ub: list, n_iter: int, inc_vertices: bool):

    lb = np.asarray(lb)
    ub = np.asarray(ub)

    return lhsdesign(n_samples, lb, ub, k=n_iter, include_vertices=inc_vertices)
