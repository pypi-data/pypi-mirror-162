'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-07-11 23:40:10
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-09 19:55:22
FilePath: /YXYIPR/meanfield/Zeeman.py
'''
from .EnergyTerm import EnergyTerm
# from EnergyTerm import EnergyTerm
import numpy as np


class Zeeman(EnergyTerm):
    """Zeeman energy term class
    This class defines effective field of Zeeman energy term.
    
    ``H`` is used to define the Zeeman energy term.
    
    Parameters
    ----------
    H: tuple
    External magnetic field(A/m)

    Examples
    --------
    1. Defining a three-dimensional vector field then
    initialize the Zeeman energy term
    
    >>> import discretisedfield as df
    >>> region = df.Region(p1=(0, 0, 0), p2=(50e-9, 50e-9, 50e-9))
    >>> mesh = df.Mesh(region=region, cell=(10e-9, 10e-9, 10e-9))
    >>> def value_fun(point):
    ...     vec = np.random.randn(3)
    ...     unit_vec = vec / np.linalg.norm(vec)
    ...     return (unit_vec[0], unit_vec[1], unit_vec[2])
    >>> H = (0, 0, 1e3)
    >>> m = df.Field(mesh, dim=3, value=value_fun, norm=Ms)
    >>> math = Math(m.array/Ms, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
    >>> Zeeman(H)
    """

    def __init__(self, H):
        self.H = H

    def effective_field(self, m):
        """
        effective field for Zeeman energy term
        .. math::
         \vec{H}_{\text {eFF }}^{z}=\vec{H}
        
        Parameters
        ----------
        m: ndarray
        normalised magnetisation field
        
        Returns
        -------
        The effective field for Zeeman energy term of the magnetisation field
        
        Examples
        --------
        1. Calculate effective field for Zeeman energy term
        
        >>> Zeeman(H).effective_field(math)  
        """
        H_mesh = np.zeros((m.m.shape[0], m.m.shape[1], m.m.shape[2], m.dim))
        H_mesh[:, :, :, 0] = self.H[0]
        H_mesh[:, :, :, 1] = self.H[1]
        H_mesh[:, :, :, 2] = self.H[2]
        return H_mesh
