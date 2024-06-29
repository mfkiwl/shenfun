"""
Solve Helmholtz equation on the unit disc

Using polar coordinates and numerical method from:

"Efficient spectral-Galerkin methods III: Polar and cylindrical geometries",
J Shen, SIAM J. Sci Comput. 18, 6, 1583-1604

Using shenfun to map coordinates instead of
directly applying r = (t+1)/2, as in the SIAM paper.

"""
import os
from shenfun import *
from shenfun.la import SolverGeneric1ND
import sympy as sp

# Define polar coordinates using angle along first axis and radius second
theta, r = psi = sp.symbols('x,y', real=True, positive=True)
rv = (r*sp.cos(theta), r*sp.sin(theta))

alpha = 0

# Manufactured solution
ue = (r*(1-r))**2*sp.cos(8*theta)-0.1*(r-1)

N = 32
F = FunctionSpace(N, 'F', dtype='d')
F0 = FunctionSpace(1, 'F', dtype='d')
L = FunctionSpace(N, 'L', bc=(0, 0), domain=(0, 1))
L0 = FunctionSpace(N, 'L', bc=(None, 0), domain=(0, 1))
T = TensorProductSpace(comm, (F, L), axes=(1, 0), coordinates=(psi, rv))
T0 = TensorProductSpace(MPI.COMM_SELF, (F0, L0), axes=(1, 0), coordinates=(psi, rv))

v = TestFunction(T)
u = TrialFunction(T)
v0 = TestFunction(T0)
u0 = TrialFunction(T0)

# Compute the right hand side on the quadrature mesh
# f = -ue.diff(r, 2) - (1/r)*ue.diff(r, 1) - (1/r**2)*ue.diff(theta, 2) + alpha*ue
f = (-div(grad(u))+alpha*u).tosympy(basis=ue, psi=psi)
fj = Array(T, buffer=f)

# Take scalar product
f_hat = Function(T)
f_hat = inner(v, fj, output_array=f_hat)
if T.local_slice(True)[0].start == 0: # The processor that owns k=0
    f_hat[0] = 0

# For m=0 we solve only a 1D equation. Do the scalar product for Fourier coefficient 0 by hand (or sympy)
# Since F0 only has one item, it is not sufficient to do a numerical inner product.
if comm.Get_rank() == 0:
    f0_hat = Function(T0)
    gt = sp.lambdify(r, sp.integrate(f, (theta, 0, 2*sp.pi))/2/sp.pi)(L0.mesh())
    f0_hat = T0.scalar_product(gt, f0_hat)

# Assemble matrices.
mats = inner(v, -div(grad(u))+alpha*u)
# case m=0
if comm.Get_rank() == 0:
    mats0 = inner(v0, -div(grad(u0))+alpha*u0)

# Solve
# case m > 0
u_hat = Function(T)
Sol1 = SolverGeneric1ND(mats)
u_hat = Sol1(f_hat, u_hat)

# case m = 0
u0_hat = Function(T0)
if comm.Get_rank() == 0:
    Sol0 = SolverGeneric1ND(mats0)
    u0_hat = Sol0(f0_hat, u0_hat)
comm.Bcast(u0_hat, root=0)

# Transform back to real space. Broadcast 1D solution
sl = T.local_slice(False)
uj = u_hat.backward() + u0_hat.backward()[:, sl[1]]
uq = Array(T, buffer=ue)
err = np.sqrt(inner(1, (uj-uq)**2))
print('Error =', err)
assert err < 1e-8

# Find and plot gradient of u. For this we need a space without
# boundary conditions, and a vector space
#LT = FunctionSpace(N, 'L', domain=(0, 1))
#TT = TensorProductSpace(comm, (F, LT), axes=(1, 0), coordinates=(psi, rv))
TT = T.get_orthogonal()
V = VectorSpace(TT)
# Get solution on space with no bc
ua = Array(TT, buffer=uj)
uh = ua.forward()
dv = project(grad(uh), V)
du = dv.backward()
# The gradient du now contains the contravariant components of basis
# b. Note that basis b is not normalized (it is not a unity vector)
# To get unity vector (regular polar unit vectors), do
#    e = b / T.hi[:, None]

# Exact gradient in computational basis
gradue = Array(V, buffer=grad(u).tosympy(basis=ue, psi=psi))
# Compute error sqrt(inner(|grad(u)-grad(ue)|**2))
gij = T.coors.get_covariant_metric_tensor()
ui, vi = TT.local_mesh(True, kind='uniform')
# Evaluate metric on computational mesh
gij[0, 0] = np.array(sp.lambdify(psi, gij[0, 0])(ui, vi), dtype=object)
errorg = inner(1, (du[0]-gradue[0])**2*gij[0, 0]+ (du[1]-gradue[1])**2*gij[1, 1])
print('Error gradient = %2.6e'%(np.sqrt(float(errorg))))
assert np.sqrt(float(errorg)) < 1e-7

if 'pytest' not in os.environ:
    import matplotlib.pyplot as plt

    # Postprocess
    # Refine for a nicer plot. Refine simply pads Functions with zeros, which
    # gives more quadrature points. u_hat has NxN quadrature points, refine
    # using any higher number.
    u_hat2 = u_hat.refine([N*3, N*3])
    u0_hat2 = u0_hat.refine([1, N*3])
    sl = u_hat2.function_space().local_slice(False)
    ur = u_hat2.backward() + u0_hat2.backward()[:, sl[1]]

    # Wrap periodic plot around since it looks nicer
    xx, yy = u_hat2.function_space().local_cartesian_mesh()
    xp = np.vstack([xx, xx[0]])
    yp = np.vstack([yy, yy[0]])
    up = np.vstack([ur, ur[0]])
    # For vector:
    xi, yi = TT.local_cartesian_mesh()

    # plot
    plt.figure()
    plt.contourf(xp, yp, up)
    b = T.coors.get_covariant_basis()
    #bij = np.array(sp.lambdify(psi, b)(ui, vi)) # no longer allowed in sympy
    bij = np.zeros((2, 2, N, N))
    for i in (0, 1):
        for j in (0, 1):
            bij[i, j] = sp.lambdify(psi, b[i, j])(ui, vi)
    # Compute Cartesian gradient
    gradu = du[0]*bij[0] + du[1]*bij[1]
    plt.quiver(xi, yi, gradu[0], gradu[1], scale=40, pivot='mid', color='white')
    plt.colorbar()
    plt.title('Helmholtz - unitdisc')
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')
    plt.show()
cleanup(vars())