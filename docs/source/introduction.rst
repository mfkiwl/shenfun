Introduction
============

Spectral Galerkin
-----------------

The spectral Galerkin method solves partial differential equations through
a special form of the `method of weighted residuals <https://en.wikiversity.org/wiki/Introduction_to_finite_elements/Weighted_residual_methods>`_ (WRM). As a Galerkin method it
is very similar to the `finite element method <https://en.wikipedia.org/wiki/Finite_element_method>`_ (FEM). The most distinguishable
feature is that it uses global shape functions, where FEM uses local. This
feature leads to highly accurate results with very few shape functions, but
the downside is much less flexibility when it comes to computational
domain than FEM.

Consider the Poisson equation with a right hand side function :math:`f(\boldsymbol{x})`

.. math::
   :label: eq:poisson1

    -\nabla^2 u(\boldsymbol{x}) = f(\boldsymbol{x}) \quad \text{for } \, \boldsymbol{x} \in \Omega.

To solve this equation, we will eventually need to supplement
appropriate boundary conditions. However, for now just assume that any valid
boundary conditions (Dirichlet, Neumann, periodic) apply.

With the method of weighted residuals we attempt to find :math:`u(\boldsymbol{x})`
using an approximation, :math:`u_N`, to the solution

.. math::
   :label: eq:mwr_u

    u(\boldsymbol{x}) \approx u_N(\boldsymbol{x}) = \sum_{k=0}^{N-1} \hat{u}_k \phi_k(\boldsymbol{x}).

Here the :math:`N` expansion coefficients :math:`\{\hat{u}_k\}` are unknown
and :math:`\{\phi_k\}` are a set of
*basis* (or *trial*) functions. The basis functions form a basis for the discrete
(finite-dimensional) function space

.. math::

    V_N = \text{span}\{\phi_k\}_{k=0}^{N-1},

and by :eq:`eq:mwr_u` we express that :math:`u \approx u_N \in V_N`.

Inserting for :math:`u_N` in Eq. :eq:`eq:poisson1` we get a residual

.. math::
   :label: eq:residual

    R_N(\boldsymbol{x}) = \nabla^2 u_N(\boldsymbol{x}) + f(\boldsymbol{x}) \neq 0.

With the WRM we now force this residual to zero in an average sense using
*test* function :math:`v(\boldsymbol{x})` and *weight* function
:math:`w(\boldsymbol{x})`

.. math::
   :label: eq:wrm_test

    \left(R_N, v \right)_w := \int_{\Omega} R_N(\boldsymbol{x}) \, \overline{v}(\boldsymbol{x}) \, w(\boldsymbol{x}) d\boldsymbol{x} = 0,

where :math:`\overline{v}` is the complex conjugate of :math:`v`. If we
now choose the test functions from the same space as the trial functions,
i.e., :math:`V_N`,
then the WRM becomes the Galerkin method, and we get :math:`N` equations for
:math:`N` unknowns :math:`\{\hat{u}_j\}`

.. math::
   :label: eq:galerkin

    \sum_{j=0}^{N-1} \underbrace{\left(-\nabla^2 \phi_j, \phi_k \right)_w}_{a_{kj}} \hat{u}_j = \left( f, \phi_k \right)_w, \quad k =0, 1, \ldots, N-1.

Note that this is a regular system of linear algebra equations to be solved for
the column vector :math:`\boldsymbol{\hat{u}} = (\hat{u}_0, \hat{u}_1, \ldots, \hat{u}_{N-1})^T \in \mathbb{R}^N`

.. math::

    A \boldsymbol{\hat{u}} = \boldsymbol{\tilde{f}},

where :math:`A=(a_{kj}) \in \mathbb{R}^{N \times N}` is a matrix, :math:`\tilde{f}_k = \left( f, \phi_k \right)_w`
and :math:`\boldsymbol{\tilde{f}} = (\tilde{f}_0, \tilde{f}_1, \ldots, \tilde{f}_{N-1})^T` :math:`\in \mathbb{R}^N`
is a column vector.

The choice of basis functions, or function space :math:`V_N`,
is highly central to the method.
For the Galerkin method to be *spectral*, the basis is usually chosen as linear
combinations of Chebyshev, Legendre, Laguerre, Hermite, Jacobi or trigonometric functions.
In one spatial dimension typical choices for :math:`\phi_k` are

.. math::

   \phi_k(x) &= T_k(x) \\
   \phi_k(x) &= T_k(x) - T_{k+2}(x) \\
   \phi_k(x) &= L_k(x) \\
   \phi_k(x) &= L_k(x) - L_{k+2}(x) \\
   \phi_k(x) &= \exp(\imath k x)

where :math:`T_k, L_k` are the :math:`k`'th Chebyshev polynomial of the first
kind and the :math:`k`'th Legendre polynomial, respectively. Note that the
second and fourth functions above satisfy the homogeneous Dirichlet boundary
conditions :math:`\phi_k(\pm 1) = 0`, and as such these basis functions may be
used to solve the Poisson equation :eq:`eq:poisson1` with homogeneous Dirichlet
boundary conditions. Similarly, two basis functions that satisfy homogeneous
Neumann boundary condition :math:`u'(\pm 1)=0` are

.. math::

    \phi_k &= T_k-\left(\frac{k}{k+2}\right)^2T_{k+2} \\
    \phi_k &= L_k-\frac{k(k+1)}{(k+2)(k+3)}L_{k+2}

Shenfun contains classes for working with several such bases, to be used for
different equations and boundary conditions. More precisely, for a
problem at hand the user chooses a function space, :math:`V_N`.
Associated with the function space is a
domain (e.g., :math:`[-1, 1]`), and a weighted inner product. The weights
:math:`w(x)` are chosen under the hood, and specifically for each basis. For example,
Chebyshev functions use the weight :math:`1/\sqrt{1-x^2}`, whereas Legendre
and Fourier functions use a constant weight.


Tensor products
---------------

If the physical problem at hand is two-dimensional, then we need to approximate two-dimensional
functions like :math:`u(x, y)`. To this end we need to use two one-dimensional function spaces
and then combine them through tensor products in order to get a two-dimensional (tensor product) space.
For example, if we choose the function spaces
:math:`X_N` and :math:`Y_M`, for the first and second dimension, respectively,
then we can create a 2D tensor product space :math:`W_P` as

.. math::

    W_{P} = X_N \otimes Y_M,

where the dimension :math:`P=N \cdot M` and :math:`\otimes` represents a tensor product.
See, e.g., this `tensor product blog`_ for a simple explanation of the
tensor product.

Two generic bases for :math:`X_N` and :math:`Y_M` will be

.. math::

    \{ \mathcal{X}_j(x) \}_{j \in \mathcal{I}^N} \text{ and } \{ \mathcal{Y}_k(y) \}_{k \in \mathcal{I}^M},

where the index set :math:`\mathcal{I}^N=\{0, 1, \ldots, N-1\}`
and :math:`\mathcal{X}_j(x)` and :math:`\mathcal{Y}_k(y)` are some appropriately
chosen basis functions. Note that we are here using the
:math:`y`-coordinate for the
:math:`Y_M` basis, because this basis is used along the
second axis of the tensor product space :math:`W_P`.

We may now also define the tensor product space :math:`W_P` as

.. math::

    W_P = \text{span}\{ \mathcal{X}_j(x) \mathcal{Y}_k(y) \}_{(j, k) \in \mathcal{I}^N \times \mathcal{I}^M},

where :math:`\times` represents a Cartesian product. A basis function for
:math:`W_P` may as such be written as

.. math::

   v_{jk}(x, y) = \mathcal{X}_j(x) \mathcal{Y}_k(y),

and if we now want to approximate :math:`u(x, y) \approx u_N(x, y) \in W_P` this means that
we intend to find

.. math::

    u_N(x, y) = \sum_{i\in \mathcal{I}^N}\sum_{j\in \mathcal{I}^M} \hat{u}_{ij} \mathcal{X}_i(x) \mathcal{Y}_{j}(y),

where the :math:`P=N \cdot M` expansion coefficients :math:`\{\hat{u}_{ij}\}` are the unknowns.

As an example, assume now that we have a 2D Cartesian domain
:math:`\Omega = [-1, 1] \times [0, 2 \pi]`,
with homogeneous Dirichlet boundary conditions at :math:`x=\pm 1` and a
periodic solution in the :math:`y`-direction. We may now choose the basis functions
:math:`\mathcal{X}_j(x) = T_j(x)-T_{j+2}(x)`
and :math:`\mathcal{Y}_k(y) = \exp(\imath k y)` such that these boundary conditions are
satisfied exactly, and the 2D basis functions are the tensor products

.. math::
   :label: eq:v2D

   v_{jk}(x, y) = (T_j(x) - T_{j+2}(x)) \exp(\imath k y).

In other words, we choose one test function per spatial dimension and create
global basis functions by taking the outer products (or tensor products) of these individual
test functions. Since global basis functions simply are the tensor products of
one-dimensional basis functions, it is trivial to move to even higher-dimensional spaces.
The multi-dimensional basis functions then form a basis for a multi-dimensional
tensor product space. The associated domains are similarly formed by taking
Cartesian products of the one-dimensional domains.

The one-dimensional domains are discretized using the quadrature points of the
chosen basis functions. If the meshes in :math:`x`- and :math:`y`-directions are
:math:`x = (x_i)_{i\in \mathcal{I}^N}` and :math:`y = (y_j)_{j\in \mathcal{I}^M}`,
then a Cartesian product mesh is :math:`x \times y`. With index and set builder
notation it is given as

.. math::
    :label: eq:tensormesh

    x \times y = \left\{(x_i, y_j) \,|\, i \in \mathcal{I}^N \text{ and } j \in \mathcal{I}^M\right\}.

With shenfun a user chooses the appropriate function spaces (with associated bases)
for each dimension of the problem, and may then combine these bases into tensor
product spaces and Cartesian product domains. For
example, to create the required spaces for the aforementioned domain, with Dirichlet in
:math:`x`- and periodic in :math:`y`-direction, we need the following:

.. math::

    N, M &= (16, 16) \\
    X_N(x) &= \text{span}\{T_j(x)-T_{j+2}(x)\}_{j\in \mathcal{I}^{N}} \\
    Y_M(y) &= \text{span}\{\exp(\imath k y)\}_{k\in \mathcal{I}^M} \\
    W_P(x, y) &= X_N(x) \otimes Y_M(y)

This can be implemented in `shenfun` as follows::

    from shenfun import comm, FunctionSpace, TensorProductSpace
    N, M = (16, 16)
    XN = FunctionSpace(N+2, 'Chebyshev', bc=(0, 0))
    YM = FunctionSpace(M, 'Fourier', dtype='d')
    W = TensorProductSpace(comm, (XN, YM))

Note that the Chebyshev space is created using :math:`N+2` and not :math:`N`. The two
chosen boundary condition ``bc=(0, 0)`` ensures that only :math:`N` basis
functions will be used, or in other words, that the dimension of ``XN`` is :math:`N`.
The Fourier basis ``YM`` has been defined for real inputs,
which is ensured by the ``dtype`` keyword being set to ``d`` for double. ``dtype``
specifies the data type that is input to the ``forward`` method, or the
data type of the solution in physical space. Setting
``dtype='D'`` indicates that this datatype will be complex. Note that it
will not trigger an error, or even lead to wrong results, if ``dtype`` is
by mistake set to ``D``. It is merely less efficient to work with complex data
arrays where double precision is sufficient. See Sec :ref:`sec:gettingstarted`
for more information on getting started with using bases.

Shenfun is parallelized with MPI through the `mpi4py-fft`_ package.
If we store the current example in ``filename.py``, then it can be run
with more than one processor, e.g., like::

    mpirun -np 4 python filename.py

In this case the tensor product space ``W_P`` will be distributed
with the *slab* method (since the problem is 2D) and it
can here use a maximum of 9 CPUs. The maximum is 9 since the last dimension is
transformed from 16 real numbers to 9 complex, using the Hermitian symmetry of
real transforms, i.e., the shape of a transformed array in the ``W_P`` space will be
(14, 9). You can read more about MPI in the later section :ref:`MPI`.

Tribute
-------

Shenfun is named as a tribute to Prof. Jie Shen, as it contains many
tools for working with his modified Chebyshev and Legendre bases, as
described here:

    * Jie Shen, SIAM Journal on Scientific Computing, 15 (6), 1489-1505 (1994) (JS1)
    * Jie Shen, SIAM Journal on Scientific Computing, 16 (1), 74-87, (1995) (JS2)

Shenfun has implemented classes for the bases described in these papers,
and within each class there are methods for fast transforms, inner
products and for computing matrices arising from bilinear forms in the
spectral Galerkin method.

.. _shenfun: https:/github.com/spectralDNS/shenfun
.. _mpi4py-fft: https://bitbucket.org/mpi4py/mpi4py-fft
.. _Demo for the nonlinear Klein-Gordon equation: https://rawgit.com/spectralDNS/shenfun/master/docs/src/KleinGordon/kleingordon_bootstrap.html
.. _Demo for the Kuramato-Sivashinsky equation: https://rawgit.com/spectralDNS/shenfun/master/docs/src/KuramatoSivashinsky/kuramatosivashinsky_bootstrap.html
.. _Demo for Poisson equation in 1D with inhomogeneous Dirichlet boundary conditions: https://rawgit.com/spectralDNS/shenfun/master/docs/src/Poisson/poisson_bootstrap.html
.. _Demo for Poisson equation in 3D with Dirichlet in one and periodicity in remaining two dimensions: https://rawgit.com/spectralDNS/shenfun/master/docs/src/Poisson3D/poisson3d_bootstrap.html
.. _tensor product blog: https://www.math3ma.com/blog/the-tensor-product-demystified
