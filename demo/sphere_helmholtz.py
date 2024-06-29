"""
Solve Helmholtz equation on a sphere

Using spherical coordinates

"""
import os
from shenfun import *
from shenfun.la import SolverGeneric1ND
import sympy as sp

by_parts = False

# Define spherical coordinates
r = 1
theta, phi = psi = sp.symbols('x,y', real=True, positive=True)
rv = (r*sp.sin(theta)*sp.cos(phi), r*sp.sin(theta)*sp.sin(phi), r*sp.cos(theta))

alpha = 2

# Manufactured solution
sph = sp.functions.special.spherical_harmonics.Ynm
ue = sph(6, 3, theta, phi)
#ue = sp.cos(8*(sp.sin(theta)*sp.cos(phi) + sp.sin(theta)*sp.sin(phi) + sp.cos(theta)))
#g = - ue.diff(theta, 2) - (1/sp.tan(theta))*ue.diff(theta, 1) - (1/sp.sin(theta)**2)*ue.diff(phi, 2) + alpha*ue

N, M = 60, 40
L0 = FunctionSpace(N, 'C', domain=(0, np.pi))
F1 = FunctionSpace(M, 'F', dtype='D')
T = TensorProductSpace(comm, (L0, F1), coordinates=(psi, rv, sp.Q.positive(sp.sin(theta))))

v = TestFunction(T)
u = TrialFunction(T)

# Compute the right hand side on the quadrature mesh
g = (-div(grad(u))+alpha*u).tosympy(basis=ue, psi=psi)
gj = Array(T, buffer=g)

# Take scalar product
g_hat = Function(T)
g_hat = inner(v, gj, output_array=g_hat)

# Assemble matrices.
if by_parts:
    mats = inner(grad(v), grad(u))
    mats += [inner(v, alpha*u)]

else:
    mats = inner(v, -div(grad(u))+alpha*u)

# Solve
u_hat = Function(T)
Sol1 = SolverGeneric1ND(mats)
u_hat = Sol1(g_hat, u_hat)

# Transform back to real space.
uj = u_hat.backward()
uq = Array(T, buffer=ue)
error = np.sqrt(inner(1, abs((uj-uq)**2)))
print(f'sphere_helmholtz L2 error {error:2.6e}')

if 'pytest' not in os.environ:
    # Postprocess
    # Refine for a nicer plot. Refine simply pads Functions with zeros, which
    # gives more quadrature points. u_hat has NxM quadrature points, refine
    # using any higher number.
    u_hat2 = u_hat.refine([N*3, M*3])
    ur = u_hat2.backward(kind='uniform')
    surf3D(ur.real, backend='mayavi', wrapaxes=(1,))
    from mayavi import mlab
    mlab.savefig('spherewhite.png')
    mlab.show()
else:
    assert error < 1e-6

cleanup(vars())