'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-07-11 14:17:54
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-09 19:55:03
FilePath: /YXYIPR/Exchange.py
'''
# import sys
# sys.path.append("../meanfield")
# from EnergyTerm import EnergyTerm
from .EnergyTerm import EnergyTerm

class Exchange(EnergyTerm):
    """Exchange energy term class
    This class defines effective field of Exchange energy term.
    Magnetic moments will attempt to align all other atomic magnetic moments 
    which is known as the Exchange energy term
    ``A``, ``miu0``, ``Ms`` are used to define the Exchange energy term.
    
    Parameters
    ----------
    A : float, int
        The exchange energy constant
    miu0: float, int
        The permeability of free space
    Ms: float, int
        Saturation magnetisation

    Examples
    --------
    1. Defining a three-dimensional vector field then
    initialize the exchange energy term
    
    >>> import discretisedfield as df
    >>> region = df.Region(p1=(0, 0, 0), p2=(50e-9, 50e-9, 50e-9))
    >>> mesh = df.Mesh(region=region, cell=(10e-9, 10e-9, 10e-9))
    >>> def value_fun(point):
    ...     vec = np.random.randn(3)
    ...     unit_vec = vec / np.linalg.norm(vec)
    ...     return (unit_vec[0], unit_vec[1], unit_vec[2])
    >>> Ms =  8e5
    >>> A = 8.78e-12
    >>> miu0 = 12.57*1e-7
    >>> m = df.Field(mesh, dim=3, value=value_fun, norm=Ms)
    >>> math = Math(m.array/Ms, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
    >>> Exchange(A, miu0, Ms)
    """

    def __init__(self, A, miu0, Ms):
        self.A = A
        self.miu0 = miu0
        self.Ms = Ms

    def effective_field(self, m):
        """
        effective field for exchange energy term
        .. math::
        \\vec{H}_{\\text {ex }}=\\frac{2 A}{\\mu_{0} M_{s}} \\nabla^{2} \\vec{m}
        
        Parameters
        ----------
        m: ndarray
        normalised magnetisation field
        
        Returns
        -------
        The effective field for exchange energy term of the magnetisation field
        
        Examples
        --------
        1. Calculate effective field for exchange energy term
        
        >>> Exchange(A, miu0, Ms).effective_field(math)
            
        """
        return (2*self.A * m.laplace()) / (self.miu0 * self.Ms)
