r"""Solve Poisson's equation using a mixed formulation

The Poisson equation is

.. math::

    \nabla^2 u &= f \\
    u(x, y=\pm 1) &= 0 \\
    u(x=2\pi, y) &= u(x=0, y)

We solve using the mixed formulation

.. math::

    g - \nabla(u) &= 0 \\
    \nabla \cdot g &= f \\
    u(x, y=\pm 1) &= 0 \\
    u(x=2\pi, y) &= u(x=0, y) \\
    g(x=2\pi, y) &= g(x=0, y)

We use a Tensorproductspace with Fourier expansions in the x-direction and
a composite Chebyshev basis in the y-direction. The equations are solved
coupled and implicit.

"""

import os
import sys
import numpy as np
from sympy import symbols, sin, cos
from shenfun import *

x, y = symbols("x,y", real=True)

# Create a manufactured solution for verification
#ue = (sin(2*x)*cos(3*y))*(1-x**2)
ue = (sin(4*x)*cos(5*y))*(1-y**2)
dux = ue.diff(x, 1)
duy = ue.diff(y, 1)
fe = ue.diff(x, 2) + ue.diff(y, 2)

def main(N, family):
    K0 = FunctionSpace(N, 'Fourier', dtype='d')
    SD = FunctionSpace(N, family, bc=(0, 0))
    ST = FunctionSpace(N, family)

    TD = TensorProductSpace(comm, (K0, SD), axes=(1, 0))
    TT = TensorProductSpace(comm, (K0, ST), axes=(1, 0))
    VT = VectorSpace(TT)
    Q = CompositeSpace([VT, TD])

    gu = TrialFunction(Q)
    pq = TestFunction(Q)

    g, u = gu
    p, q = pq

    A00 = inner(p, g)
    if family == 'legendre':
        A01 = inner(div(p), u)
    else:
        A01 = inner(p, -grad(u))
    A10 = inner(q, div(g))

    # Get f and g on quad points
    vfj = Array(Q, buffer=(0, 0, fe))
    vj, fj = vfj

    vf_hat = Function(Q)
    v_hat, f_hat = vf_hat
    f_hat = inner(q, fj, output_array=f_hat)

    M = BlockMatrix(A00+A01+A10)

    gu_hat = M.solve(vf_hat)
    gu = gu_hat.backward()

    g_, u_ = gu

    uj = Array(TD, buffer=ue)
    duxj = Array(TT, buffer=dux)
    duyj = Array(TT, buffer=duy)

    error = [np.sqrt(inner(1, (uj-u_)**2)),
             np.sqrt(inner(1, (duxj-g_[0])**2)),
             np.sqrt(inner(1, (duyj-g_[1])**2))]

    if 'pytest' not in os.environ:
        import matplotlib.pyplot as plt
        plt.figure()
        X = TD.local_mesh(True)
        plt.contourf(X[0], X[1], u_)
        plt.figure()
        plt.quiver(X[1], X[0], g_[1], g_[0])
        plt.figure()
        plt.spy(M.diags(0, format='csr').toarray()) # The matrix for given Fourier wavenumber
        plt.show()
    else:
        if comm.Get_rank() == 0:
            print(SD.family())
            print('    L2 error      u       dudx       dudy')
            print('         %2.4e %2.4e %2.4e' %(error[0], error[1], error[2]))
        assert np.all(abs(np.array(error)) < 1e-8), error
    Q.destroy()

if __name__ == '__main__':
    for family in ('CLUQJ'):
        main(24, family)
