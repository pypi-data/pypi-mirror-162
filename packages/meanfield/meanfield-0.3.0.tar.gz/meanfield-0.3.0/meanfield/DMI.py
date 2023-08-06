'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-07-11 21:13:32
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-09 19:54:56
FilePath: /YXYIPR/meanfield/DMI.py

'''
from .EnergyTerm import EnergyTerm
# from EnergyTerm import EnergyTerm


class DMI(EnergyTerm):
    """Dzyaloshinskii-Moriya energy term class
    This class defines effective field of Dzyaloshinskii-Moriya(DMI) energy term.
    
    ``D``, ``miu0``, ``Ms`` are used to define the Dzyaloshinskii-Moriya energy term.
    
    Parameters
    ----------
    D : float, int
        DMI energy constant
    miu0: float, int
        the permeability of free space
    Ms: float, int
        Saturation magnetisation

    Examples
    --------
    1. Defining a three-dimensional vector field then
    initialize the DMI energy term
    
    >>> import discretisedfield as df
    >>> region = df.Region(p1=(0, 0, 0), p2=(50e-9, 50e-9, 50e-9))
    >>> mesh = df.Mesh(region=region, cell=(10e-9, 10e-9, 10e-9))
    >>> def value_fun(point):
    ...     vec = np.random.randn(3)
    ...     unit_vec = vec / np.linalg.norm(vec)
    ...     return (unit_vec[0], unit_vec[1], unit_vec[2])
    >>> Ms =  8e5
    >>> D = 1e-3
    >>> miu0 = 12.57*1e-7
    >>> m = df.Field(mesh, dim=3, value=value_fun, norm=Ms)
    >>> math = Math(m.array/Ms, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
    >>> DMI(D, miu0, Ms=Ms)
    """
    def __init__(self, D, miu0, Ms):
        self.D = D
        self.miu0 = miu0
        self.Ms = Ms

    def effective_field(self, m):
        """
        effective field for DMI energy term
        .. math::
         \vec{H}_{\text {eFF }}^{DMI}=\frac{-2 D}{u_{0} M_{s}}(\nabla \times \vec{m})
        
        Parameters
        ----------
        m: ndarray
        normalised magnetisation field
        
        Returns
        -------
        The effective field for DMI energy term of the magnetisation field
        
        Examples
        --------
        1. Calculate effective field for DMI energy term
        
        >>> DMI(D, miu0, Ms=Ms).effective_field(math)  
        """
        return (-2 * self.D * m.curl()) / (
            self.miu0 * self.Ms)
