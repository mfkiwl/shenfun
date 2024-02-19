"""
Solve the Orr-Sommerfeld eigenvalue problem

Using Shen's biharmonic basis

"""
import warnings
from scipy.linalg import eig
#from numpy.linalg import eig
#from numpy.linalg import inv
import numpy as np
import sympy as sp
from shenfun import FunctionSpace, Function, Dx, inner, TestFunction, \
    TrialFunction

np.seterr(divide='ignore')

#pylint: disable=no-member

try:
    from matplotlib import pyplot as plt

except ImportError:
    warnings.warn("matplotlib not installed")

x = sp.Symbol('x', real=True)

class OrrSommerfeld:
    def __init__(self, alfa=1., Re=8000., N=80, quad='GC', test='G', trial='G', **kwargs):
        kwargs.update(dict(alfa=alfa, Re=Re, N=N, quad=quad, test=test, trial=trial))
        vars(self).update(kwargs)
        self.x, self.w = None, None
        assert self.trial in ('PG', 'G')
        assert self.test in ('PG', 'G')

    def interp(self, y, eigvals, eigvectors, eigval=1, verbose=False):
        """Interpolate solution eigenvector and it's derivative onto y

        Parameters
        ----------
            y : array
                Interpolation points
            eigvals : array
                All computed eigenvalues
            eigvectors : array
                All computed eigenvectors
            eigval : int, optional
                The chosen eigenvalue, ranked with descending imaginary
                part. The largest imaginary part is 1, the second
                largest is 2, etc.
            verbose : bool, optional
                Print information or not
        """
        nx, eigval = self.get_eigval(eigval, eigvals, verbose)
        if self.trial == 'G':
            SB = FunctionSpace(self.N, 'C', bc=(0, 0, 0, 0), quad=self.quad, dtype='D')
        else:
            SB = FunctionSpace(self.N, 'C', basis='Phi2', quad=self.quad, dtype='D')
        phi_hat = Function(SB)
        phi_hat[:-4] = np.squeeze(eigvectors[:, nx])
        phi = phi_hat.eval(y)
        dphidy = Dx(phi_hat, 0, 1).eval(y)
        return eigval, phi, dphidy

    def get_trialspace(self, trial, dtype='d'):
        if trial == 'G':
            return FunctionSpace(self.N, 'C', basis='ShenBiharmonic', quad=self.quad, dtype=dtype)
        return FunctionSpace(self.N, 'C', basis='Phi2', quad=self.quad, dtype=dtype)

    def get_testspace(self, trial):
        return trial.get_testspace(self.test)

    def assemble(self, scale=None):
        trial = self.get_trialspace(self.trial)
        test = trial.get_testspace(self.test)
        v = TestFunction(test)
        u = TrialFunction(trial)

        Re = self.Re
        a = self.alfa
        g = 1j*a*Re

        # (u'', v)_w
        K = inner(v, Dx(u, 0, 2))

        # ((1-x**2)u, v)_w
        K1 = inner(v*(1-x**2), u)

        # ((1-x**2)u'', v)_w
        K2 = inner(v*(1-x**2), Dx(u, 0, 2))

        # (u'''', v)_w
        Q = inner(v, Dx(u, 0, 4))

        # (u, v)_w
        M = inner(v, u)

        B = -Re*a*1j*(K-a**2*M)
        A = Q-2*a**2*K+(a**4 - 2*a*Re*1j)*M - 1j*a*Re*(K2-a**2*K1)

        # Alternatively:
        #A1 = lambda f: Dx(f, 0, 4)-2*a**2*Dx(f, 0, 2)+(a**4-2*g)*f-g*(1-x**2)*(Dx(f, 0, 2)-f)
        #B1 = lambda f: -g*(Dx(f, 0, 2)-f)
        #A = inner(A1(u), v)
        #B = inner(B1(u), v)
        #A = sum(A[1:], A[0])
        #B = sum(B[1:], B[0])
        A, B = A.diags().toarray(), B.diags().toarray()

        if scale is not None and not (scale[0] == 0 and scale[1] == 0):
            assert isinstance(scale, tuple)
            assert len(scale) == 2
            s0, s1 = scale
            k = np.arange(self.N-4)
            testp = 1/(k+1)**(-s0) if s0 < 0 else (k+1)**s0
            trialp = 1/(k+1)**(-s1) if s1 < 0 else (k+1)**s1
            d =  testp[:, None] * trialp[None, :]
            ##d = (1/A.diagonal())[:, None]
            A *= d # * A
            B *= d # * B
        return A, B

    def solve(self, verbose=False, scale=None):
        """Solve the Orr-Sommerfeld eigenvalue problem
        """
        if verbose:
            print('Solving the Orr-Sommerfeld eigenvalue problem...')
            print('Re = '+str(self.Re)+' and alfa = '+str(self.alfa))
        A, B = self.assemble(scale=scale)
        return eig(A, B)
        # return eig(np.dot(inv(B), A))

    @staticmethod
    def get_eigval(nx, eigvals, verbose=False):
        """Get the chosen eigenvalue

        Parameters
        ----------
            nx : int
                The chosen eigenvalue. nx=1 corresponds to the one with the
                largest imaginary part, nx=2 the second largest etc.
            eigvals : array
                Computed eigenvalues
            verbose : bool, optional
                Print the value of the chosen eigenvalue. Default is False.

        """
        indices = np.argsort(np.imag(eigvals))
        indi = indices[-1*np.array(nx)]
        eigval = eigvals[indi]
        if verbose:
            ev = list(eigval) if np.ndim(eigval) else [eigval]
            indi = list(indi) if np.ndim(indi) else [indi]
            for i, (e, v) in enumerate(zip(ev, indi)):
                print('Eigenvalue {} ({}) = {:2.16e}'.format(i+1, v, e))
        return indi, eigval

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Orr Sommerfeld parameters')
    parser.add_argument('--N', type=int, default=400,
                        help='Number of discretization points')
    parser.add_argument('--Re', default=8000.0, type=float,
                        help='Reynolds number')
    parser.add_argument('--alfa', default=1.0, type=float,
                        help='Parameter')
    parser.add_argument('--quad', default='GC', type=str, choices=('GC', 'GL', 'LG'),
                        help='Discretization points: GC: Gauss-Chebyshev, GL: Gauss-Lobatto')
    parser.add_argument('--test', default='G', type=str,
                        help='G or PG, Galerkin or Petrov-Galerkin')
    parser.add_argument('--trial', default='G', type=str,
                        help='G or PG, Galerkin or Petrov-Galerkin')
    parser.add_argument('--plot', dest='plot', action='store_true', help='Plot eigenvalues')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Print results')
    parser.set_defaults(plot=False)
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    #z = OrrSommerfeld(N=120, Re=5772.2219, alfa=1.02056)
    z = OrrSommerfeld(**vars(args))
    evals, evectors = z.solve(args.verbose)
    d = z.get_eigval(1, evals, args.verbose)

    if args.Re == 8000.0 and args.alfa == 1.0 and args.N > 80:
        assert abs(d[1] - (0.24707506017508621+0.0026644103710965817j)) < 1e-12

    if args.plot:
        plt.figure()
        evi = evals*z.alfa
        plt.plot(evi.imag, evi.real, 'o')
        plt.axis([-10, 0.1, 0, 1])
        plt.show()
