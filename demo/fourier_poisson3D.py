r"""
Solve Poisson equation on (0, 2pi)x(0, 2pi)x(0, 2pi) with periodic bcs

    \nabla^2 u = f,

Use Fourier basis and find u in VxVxV such that

    (v, div(grad(u))) = (v, f)    for all v in VxVxV

where V is the Fourier basis span{exp(1jkx)}_{k=-N/2}^{N/2-1} and
VxVxV is a tensorproductspace.

"""
import os
from sympy import symbols, cos, sin, lambdify
import numpy as np
from shenfun import inner, div, grad, TestFunction, TrialFunction, FunctionSpace, \
    TensorProductSpace, Array, Function, comm, la

# Use sympy to compute a rhs, given an analytical solution
x, y, z = symbols("x,y,z", real=True)
ue = cos(4*x) + sin(4*y) + sin(6*z)
fe = ue.diff(x, 2) + ue.diff(y, 2) + ue.diff(z, 2)

# Size of discretization
N = (14, 15, 16)

K0 = FunctionSpace(N[0], 'F', dtype='D')
K1 = FunctionSpace(N[1], 'F', dtype='D')
K2 = FunctionSpace(N[2], 'F', dtype='d')
T = TensorProductSpace(comm, (K0, K1, K2))
u = TrialFunction(T)
v = TestFunction(T)

# Get f on quad points
fj = Array(T, buffer=fe)

# Compute right hand side
f_hat = Function(T)
f_hat = inner(v, fj, output_array=f_hat)

# Solve Poisson equation
A = inner(v, div(grad(u)))
sol = la.SolverDiagonal(A)
u_hat = Function(T)
u_hat = sol(f_hat, u_hat, constraints=((0, 0),))

uq = u_hat.backward()

uj = Array(T, buffer=ue)
error = np.sqrt(inner(1, (uj-uq)**2))
assert abs(error) < 1e-6
if comm.Get_rank() == 0:
    print(f"fourier_poisson3D L2 error = {abs(error):2.6e}")

# Test eval at point
point = np.array([[0.1, 0.5], [0.5, 0.6], [0.1, 0.2]])
p = T.eval(point, u_hat)
ul = lambdify((x, y, z), ue)
assert np.allclose(p, ul(*point))
p2 = u_hat.eval(point)
assert np.allclose(p2, ul(*point))

if 'pytest' not in os.environ:
    import matplotlib.pyplot as plt
    plt.figure()
    X = T.local_mesh(True) # With broadcasting=True the shape of X is local_shape, even though the number of datapoints are still the same as in 1D
    plt.contourf(X[0][:, :, 0], X[1][:, :, 0], uq[:, :, 0])
    plt.colorbar()
    plt.figure()
    plt.contourf(X[0][:, :, 0], X[1][:, :, 0], uj[:, :, 0])
    plt.colorbar()
    plt.figure()
    plt.contourf(X[0][:, :, 0], X[1][:, :, 0], uq[:, :, 0]-uj[:, :, 0])
    plt.colorbar()
    plt.title('Error')
    plt.show()

T.destroy()