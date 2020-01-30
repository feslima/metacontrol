import numpy as np
import scipy as sp

_FINFO = np.finfo(float)
_EPS = _FINFO.eps


def cholmod(A):
    """Modified Cholesky factorization

    `R = cholmod(A)` returns the upper Cholesky factor of `A` (same as `chol`)
    if `A` is (sufficiently) positive definite, and otherwise returns a
    modified factor `R` with diagonal entries `>= sqrt(delta)` and
    offdiagonal entries `<= beta` in absolute value,
    where `delta` and `beta` are defined in terms of size of diagonal and
    offdiagonal entries of A and the machine precision; see below.
    The idea is to ensure that `E = A - R'*R` is reasonably small if `A` is
    not too far from being indefinite.  If `A` is sparse, so is `R.
    The output parameter indef is set to 0 if `A` is sufficiently positive
    definite and to 1 if the factorization is modified.

    The point of modified Cholesky is to avoid computing eigenvalues,
    but for dense matrices, MODCHOL takes longer than calling the built-in
    EIG, because of the cost of interpreting the code, even though it
    only has one loop and uses vector operations.

    reference: Nocedal and Wright, Algorithm 3.4 and subsequent discussion
    (not Algorithm 3.5, which is more complicated)
    original algorithm is due to Gill and Murray, 1974
    written by M. Overton, overton@cs.nyu.edu, last modified Feb 2005

    convenient to work with A = LDL' where D is diagonal, L is unit
    lower triangular, and so R = (LD^(1/2))'

    Notes
    -----
    This code is from PyMMF Package from Michael Forbes, all credits to him! available at: https://bitbucket.org/mforbes/pymmf
    This function is located inside the script :  "mmf.math.linalg.cholesky.gmw81"
    This is based on the following MATLAB code from Michael
    L. Overton: http://cs.nyu.edu/overton/g22_opt/codes/cholmod.m
    ::
        function [R, indef, E] = cholmod(A)
        if sum(sum(abs(A-A'))) > 0
            error('A is not symmetric')
        end

        % set parameters governing bounds on L and D (eps is machine epsilon)

        n = length(A);
        diagA = diag(A);
        gamma = max(abs(diagA));             % max diagonal entry
        xi = max(max(abs(A - diag(diagA))));  % max offidagonal entry
        delta = eps*(max([gamma+xi, 1]));
        beta = sqrt(max([gamma, xi/n, eps]));
        indef = 0;

        % initialize d and L

        d = zeros(n,1);
        if issparse(A)
            L = speye(n);  % sparse identity
        else
            L = eye(n);
        end

        % there are no inner for loops, everything implemented with
        % vector operations for a reasonable level of efficiency

        for j = 1:n
            K = 1:j-1;  % column index: all columns to left of diagonal
                        % d(K) doesn't work in case K is empty
            djtemp = A(j,j) - L(j,K)*(d(K,1).*L(j,K)');   % C(j,j) in book
            if j < n
                I = j+1:n;  % row index: all rows below diagonal
                Ccol = A(I,j) - L(I,K)*(d(K,1).*L(j,K)');  % C(I,j) in book
                theta = max(abs(Ccol));
                % guarantees d(j) not too small and L(I,j) not too big
                % in sufficiently positive definite case, d(j) = djtemp
                d(j) = max([abs(djtemp), (theta/beta)^2, delta]);
                L(I,j) = Ccol/d(j);
            else
                d(j) = max([abs(djtemp), delta]);
            end
            if d(j) > djtemp  % A was not sufficiently positive definite
                indef = 1;
            end
        end
        % convert to usual output format: replace L by L*sqrt(D) and transpose
        for j=1:n
            L(:,j) = L(:,j)*sqrt(d(j));   % L = L*diag(sqrt(d)) bad in sparse case
        end;
        R = L';
        if nargout == 3
            E = A - R'*R;
        end
    """
    assert np.allclose(A, A.T)
    n = A.shape[0]
    A_diag = A.diagonal()
    gamma = abs(A_diag).max()
    xi = abs(A - np.diag(A_diag)).max()  # max offidagonal entry

    delta = _EPS * max(gamma + xi, 1)
    beta = np.sqrt(max(gamma, xi / n, _EPS))
    indef = 0

    # initialize d and L

    d = np.zeros(n, dtype=float)
    if sp.sparse.issparse(A):
        L = sp.sparse.issparse(*A.shape)
    else:
        L = np.eye(n)

    # there are no inner for loops, everything implemented with
    # vector operations for a reasonable level of efficiency

    for j in range(n):
        if j == 0:
            K = []  # column index: all columns to left of diagonal
            # d(K) doesn't work in case K is empty
        else:
            K = np.s_[:j]

        djtemp = A[j, j] - np.dot(L[j, K], d[K] * L[j, K].T)  # C(j,j) in book
        if j < n - 1:
            I = np.s_[j + 1:n]  # row index: all rows below diagonal
            Ccol = A[I, j] - np.dot(L[I, K], d[K] *
                                    L[j, K].T)  # C(I,j) in book
            theta = abs(Ccol).max()
            # guarantees d(j) not too small and L(I,j) not too big
            # in sufficiently positive definite case, d(j) = djtemp
            d[j] = max(abs(djtemp), (theta / beta) ** 2, delta)
            L[I, j] = Ccol / d[j]
        else:
            d[j] = max(abs(djtemp), delta)
        if d[j] > djtemp:  # A was not sufficiently positive definite
            indef = True

    # convert to usual output format: replace L by L*sqrt(D) and transpose
    for j in range(n):
        # L = L*diag(sqrt(d)) bad in sparse case
        L[:, j] = L[:, j] * np.sqrt(d[j])

    e = (np.dot(L, L.T) - A).diagonal()
    R = L.conj().T
    Ap = R.conj().T @ R
    return Ap, R, indef, e
