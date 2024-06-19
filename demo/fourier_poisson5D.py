r"""
Solve Poisson equation on the 5-dimensional (0, 2pi)^5 with periodic bcs

    \nabla^2 u = f,

Use Fourier basis and find u in V^5 such that

    (v, div(grad(u))) = (v, f)    for all v in V^5

where V is the Fourier space span{exp(1jkx)}_{k=-N/2}^{N/2-1} and
V^5 is a 5-dimensional tensorproductspace.

"""
import os
from sympy import symbols, cos, sin
import numpy as np
from shenfun import inner, div, grad, TestFunction, TrialFunction, FunctionSpace, \
    TensorProductSpace, Array, Function, comm, get_simplified_tpmatrices

# Use sympy to compute a rhs, given an analytical solution
x, y, z, r, s = symbols("x,y,z,r,s", real=True)
ue = cos(4*x) + sin(4*y) + sin(6*z) + cos(6*r) + sin(4*s)
fe = ue.diff(x, 2) + ue.diff(y, 2) + ue.diff(z, 2) + ue.diff(r, 2) + ue.diff(s, 2)

# Size of discretization
N = (8, 10, 12, 14, 12)

K0 = FunctionSpace(N[0], 'F', dtype='D')
K1 = FunctionSpace(N[1], 'F', dtype='D')
K2 = FunctionSpace(N[2], 'F', dtype='D')
K3 = FunctionSpace(N[3], 'F', dtype='D')
K4 = FunctionSpace(N[4], 'F', dtype='d')
T = TensorProductSpace(comm, (K0, K1, K2, K3, K4))
u = TrialFunction(T)
v = TestFunction(T)

# Get f on quad points
fj = Array(T, buffer=fe)

# Compute right hand side
f_hat = Function(T)
f_hat = inner(v, fj, output_array=f_hat)

# Solve Poisson equation
A = inner(v, div(grad(u)))
sol = get_simplified_tpmatrices(A)[0]
f_hat = sol.solve(f_hat)

uq = T.backward(f_hat)
uj = Array(T, buffer=ue)
error = np.sqrt(inner(1, (uj-uq)**2))
assert abs(error) < 1e-6
if comm.Get_rank() == 0:
    print(f"fourier_poisson5D L2 error = {abs(error):2.6e}")

if 'pytest' not in os.environ and comm.Get_size() == 1:
    import matplotlib.pyplot as plt
    plt.figure()
    X = T.local_mesh(True) # With broadcasting=True the shape of X is local_shape, even though the number of datapoints are still the same as in 1D
    plt.contourf(X[0][:, :, 0, 0, 0], X[1][:, :, 0, 0, 0], uq[:, :, 0, 0, 0])
    plt.colorbar()
    plt.figure()
    plt.contourf(X[0][:, :, 0, 0, 0], X[1][:, :, 0, 0, 0], uj[:, :, 0, 0, 0])
    plt.colorbar()
    plt.figure()
    plt.contourf(X[0][:, :, 0, 0, 0], X[1][:, :, 0, 0, 0], uq[:, :, 0, 0, 0]-uj[:, :, 0, 0, 0])
    plt.colorbar()
    plt.title('Error')
    plt.show()

T.destroy()
