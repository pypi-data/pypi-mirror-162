#!/usr/bin/env python
# coding: utf-8
import numpy as np


class Math:
    """Math class
    This class defines computational operations on discrete fields.
    When using this class, the parameters to be passed are
    ``m``, ``dim``, ``dx``, ``dy``, ``dz``.
    where ``m`` is the matrix of this discrete field,
    which is a scalar field when ``dim=1``
    and a vector field when ``dim=3``.
    ``dx``,``dy``,``dz`` are the cell size of this discrete field
    Parameters
    ----------
    m : ndarray
        Magnetisation field
    dim: int
        Dimension of the field's value
        if dim = 1, this is a scalar field 
        if dim = 3, this is a vector field
    dx: int
        Cell size of this discrete field in the x-axis direction
    dy: int
        Cell size of this discrete field in the y-axis direction
    dz: int
        Cell size of this discrete field in the z-axis direction
    
    Examples
    --------
    1. Defining a three-dimensional vector field then initialize the math class
    
    >>> import discretisedfield as df
    >>> region = df.Region(p1=(0, 0, 0), p2=(50e-9, 50e-9, 50e-9))
    >>> mesh = df.Mesh(region=region, cell=(10e-9, 10e-9, 10e-9))
    >>> def value_fun(point):
    ...     x,y,z = point
    ...     if x <= 1:
    ...         return (0,0,1)
    ...     else:
    ...         return (0,0,-1)
    >>> m = df.Field(mesh, dim=3, value=value_fun)
    >>> math = Math(m=m.array, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
    
    2. Defining a scalar field then initialize the math class
    
    >>> import discretisedfield as df
    >>> p1 = (0, 0, 0)
    >>> p2 = (2, 1, 1)
    >>> cell = (1, 1, 1)
    >>> mesh = df.Mesh(p1=p1, p2=p2, cell=cell)
    >>> m = df.Field(mesh, dim=1, value=1)
    >>> math = Math(m=m.array, dim=1, dx=1, dy=1, dz=1)

    """
    def __init__(self, m, dim, dx, dy, dz):
        self.m = m
        self.dim = dim
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def pad(self, bc, bc_input=0):
        """Magnetisation field padding
        
        This method supports padding a layer of numbers outwards
        along the edges of the matrix.
        For example, a 3*3*33 matrix becomes 5*5*5 after padding
        The padding method is specified by ``bc``, the boundary condition
        
        Parameters
        ----------
        bc : str
            boundary condition
            The input can be "pbc" or "neumann"
            "pbc": Periodic boundary conditions
            "neumann": Neumann boundary conditions
            "dirichlet": dirichlet boundary conditions
            None: No padding
        bc_input: list or int
            the input of the boundary condition
            when bc = "pbc" there is no bc_input value
            bc_input = None
            when bc = "neumann" the bc_input is int
            bc_input is the derivative or partial derivative of
            the specified function at the boundary
            when bc = "dirichlet" the bc_input is int or float or double
            bc_input is the value at the boundary
            
        Returns
        -------
        Magnetisation field after padding
        
        Examples
        --------
        1. Pad with ``dirichlet`` conditions, ``0`` is the value at the boundary
    
        >>> import discretisedfield as df
        >>> region = df.Region(p1=(0, 0, 0), p2=(50e-9, 50e-9, 50e-9))
        >>> mesh = df.Mesh(region=region, cell=(10e-9, 10e-9, 10e-9))
        >>> def value_fun(point):
        ...     x,y,z = point
        ...     if x <= 1:
        ...         return (0,0,1)
        ...     else:
        ...         return (0,0,-1)
        >>> m = df.Field(mesh, dim=3, value=value_fun)
        >>> math_1 = Math(m=m.array, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        >>> math_1.pad(bc="dirichlet", bc_input=0)
        
        2. Pad with ``pbc`` method
        
        >>> math_2 = Math(m=m.array, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        >>> math_2.pad(bc="pbc", bc_input=None)
        
        3. Pad with ``neumann`` method, ``0`` is the partial derivative 
        at the boundary
        
        >>> math_2 = Math(m=m.array, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        >>> math_2.pad(bc="neumann", bc_input=0)
        
        """
        padding = np.zeros((self.m.shape[0]+2, self.m.shape[1]+2,
                            self.m.shape[2]+2, self.dim))
        padding[1: -1, 1:-1, 1:-1, :] = self.m
        if bc == "pbc":
            # padding = np.pad(self.m, ((1,1),(1,1),(1,1),(0,0)),"wrap")
            # x direction
            padding[0, 1:-1, 1:-1, :] = self.m[-1, :, :, :]
            padding[-1, 1:-1, 1:-1, :] = self.m[0, :, :, :]
            # y direction
            padding[1:-1, 0, 1:-1, :] = self.m[:, -1, :, :]
            padding[1:-1, -1, 1:-1, :] = self.m[:, 0, :, :]
            # z direction
            padding[1:-1, 1:-1, 0, :] = self.m[:, :, -1, :]
            padding[1:-1, 1:-1, -1, :] = self.m[:, :, 0, :]
        elif bc == 'neumann':
            # padding = np.pad(self.m,((1,1),(1,1),(1,1),(0,0)),"edge")
            if bc_input == 0:
                # all boundary constant are set to 0
                bc_input = 0
            # x direction
            padding[0, 1:-1, 1:-1, ] = -bc_input * self.dx + \
                self.m[0, :, :, ]
            padding[-1, 1:-1, 1:-1, ] = bc_input * self.dx + \
                self.m[-1, :, :, ]
            # y direction
            padding[1:-1, 0, 1:-1, ] = -bc_input * self.dy +  \
                self.m[:, 0, :, ]
            padding[1:-1, -1, 1:-1, ] = bc_input * self.dy + \
                self.m[:, -1, :, ]
            # z direction
            padding[1:-1, 1:-1, 0, ] = -bc_input * self.dz + \
                self.m[:, :, 0, ]
            padding[1:-1, 1:-1, -1, ] = bc_input * self.dz + \
                self.m[:, :, -1, ]
        elif bc == 'dirichlet':
            # x direction
            padding[0, 1:-1, 1:-1, ] = bc_input*np.ones_like(
                self.m[0, :, :, ])
            padding[-1, 1:-1, 1:-1, ] = bc_input*np.ones_like(
                self.m[-1, :, :, ])
            # y direction
            padding[1:-1, 0, 1:-1, ] = bc_input*np.ones_like(
                self.m[:, 0, :, ])
            padding[1:-1, -1, 1:-1, ] = bc_input*np.ones_like(
                self.m[:, -1, :, ])
            # z direction
            padding[1:-1, 1:-1, 0, ] = bc_input*np.ones_like(
                self.m[:, :, 0, ])
            padding[1:-1, 1:-1, -1, ] = bc_input*np.ones_like(
                self.m[:, :, -1, ])
        elif bc is None:
            return self.m
        return padding

    def derivative(self, direction, n, bc, bc_input=0):
        """Directional derivative fuction
        
        This function calculates the directional derivative of a discrete field.
        The direction can be ``x`` or ``y`` or ``z``.
        The order in this function is either the first order derivative or the second order derivative,
        as determined by ``n``.
        Note that the derivative is usually preceded by the ``pad(self, bc, bc_input=0)``function,
        and the result of the derivative is also closely related to the pad function,
        , using different boundary conditions yields different derivative results
        Parameters
        ----------
        direction : str
            The direction in which the derivative is computed.
            The input can be ``x``or ``y``or ``z``
        n : int
            The order of the derivative.
            The input can be 1 or 2 
        bc : str
            boundary condition
            The input can be "pbc" or "neumann"
            "pbc": Periodic boundary conditions
            "neumann": Neumann boundary conditions
            "dirichlet": dirichlet boundary conditions
            None: No padding
        bc_input: list or int
            the input of the boundary condition
            when bc = "pbc" there is no bc_input value
            bc_input = None
            when bc = "neumann" the bc_input is int
            bc_input is the derivative or partial derivative of
            the specified function at the boundary
            when bc = "dirichlet" the bc_input is int or float or double
            bc_input is the value at the boundary
            
        Returns
        -------
        Magnetisation field after calculating the directional derivative
            
        Examples
        --------
        1. To calculate the first-order derivative in the x-direction,
        we choose the boundary condition used is periodic boundary conditions
        and we choose math:`f(x, y, z) = 2x + y`.
        We expect the derivative in the x-direction to be to be a constant scalar field
        :math:`df/dx = 2`.
        Note that we need to ignore the value of the boundary
                
        >>> import discretisedfield as df
        >>> region = df.Region(p1=(0, 0, 0), p2=(10, 10, 10))
        >>> mesh = df.Mesh(region=region, cell=(2, 2, 2))
        >>> def value_fun(point):
        ...     x, y, z = point
        ...     return 2*x + y
        >>> m = df.Field(mesh, dim=1, value=value_fun)
        >>> math_1 = Math(m=m.array, dim=1, dx=2, dy=2, dz=2)
        >>> deri = math_1.derivative(direction="x", n=1,bc="pbc", bc_input=None)
        
        Check the derivative value
        
        >>> average = deri[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> assert np.allclose(average, 2)
    
        
        2. To calculate the second-order derivative of the vector field,
        we choose the boundary condition used is periodic boundary conditions
        and we choose math:`f(x, y, z) = (z^{2}, 3x+1, y^{2})`.
        Accordingly, we expect the directional derivatives to be:
        :math:`df/dx = (0, 0, 0)`,
        :math:`df/dy=(0, 0, 2)`,
        :math:`df/dz = (2, 0, 0)`
        Note that we need to ignore the value of the boundary
        
        >>> mesh = df.Mesh(region=df.Region(
        ... p1=(0, 0, 0),
        ... p2=(100e-9, 100e-9, 100e-9)),
        ... cell=(10e-9, 10e-9, 10e-9))
        >>> def value_fun(point):
        ...     x, y, z = point
        ...     return (z**2, 3*x+1, y**2)
        >>> math_2 = Math(m=m.array, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        >>> derivative_x = math_2.derivative(direction="x", n=2,
                                              bc="pbc", bc_input=None)
        >>> derivative_y = math_2.derivative(direction="y", n=2,
                                              bc="pbc", bc_input=None)
        >>> derivative_z = math_2.derivative(direction="z", n=2,
                                              bc="pbc", bc_input=None)
        
        Check the derivative value
        
        >>> aver_x = derivative_x[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> aver_y = derivative_y[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> aver_z = derivative_z[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> assert np.allclose(aver_x, (0, 0, 0))
        >>> assert np.allclose(aver_y, (0, 0, 2))
        >>> assert np.allclose(aver_z, (2, 0, 0))
        """
        padding = self.pad(bc, bc_input)
        derivative_result = np.zeros((padding.shape[0]-2, padding.shape[1]-2,
                                     padding.shape[2]-2, self.dim))
        if n == 1:
            if direction == "x":
                derivative_result[:, :, :, ] = \
                    (padding[2:, 1:-1, 1:-1, ] -
                     padding[:-2, 1:-1, 1:-1, ]) / (2*self.dx)
            elif direction == "y":
                derivative_result[:, :, :, ] = \
                    (padding[1:-1, 2:, 1:-1, ] -
                     padding[1:-1, :-2, 1:-1, ]) / (2*self.dy)
            elif direction == "z":
                derivative_result[:, :, :, ] = \
                    (padding[1:-1, 1:-1, 2:, ] -
                     padding[1:-1, 1:-1, :-2, ]) / (2*self.dz)
            return derivative_result
        elif n == 2:
            if direction == "x":
                derivative_result[:, :, :, ] = \
                    ((padding[2:, 1:-1, 1:-1, ] - 2*padding[1:-1, 1:-1, 1:-1, ]
                      + padding[:-2, 1:-1, 1:-1, ]) / (self.dx**2))
            elif direction == "y":
                derivative_result[:, :, :, ] = \
                    ((padding[1:-1, 2:, 1:-1, ] - 2*padding[1:-1, 1:-1, 1:-1, ]
                      + padding[1:-1, :-2, 1:-1, ]) / (self.dy**2))
            elif direction == "z":
                derivative_result[:, :, :, ] = \
                    ((padding[1:-1, 1:-1, 2:, ] - 2*padding[1:-1, 1:-1, 1:-1, ]
                      + padding[1:-1, 1:-1, :-2, ]) / (self.dz**2))
            return derivative_result

    def laplace(self):
        """
        The function ``laplace`` takes the second derivative of
        the array in each direction, and then adds
        them together.
        .. math::
            V^{2} f=\\frac{\\partial^{2} f}{\\partial x^{2}}
            +\\frac{\\partial^{2} f}{\\partial y^{2}}
            +\\frac{\\partial^{2} f}{\\partial z^{2}}
        Returns
        -------
        the magnetisation field after Laplace calculation
        
        Example
        -------
        1. Compute Laplacian of a contant scalar field.For a field we
        choose :math:`f(x, y, z) = 2x^{2} + 2y^{2} + 3z^{2} `.
        Accordingly, we expect the Laplacian to be
        :math:`\\nabla f = 14`.
        Note that we need to ignore the value of the boundary

        >>> import discretisedfield as df
        >>> mesh = df.Mesh(p1=(0, 0, 0), p2=(10, 10, 10), cell=(2, 2, 2))
        >>> def value_fun(point):
        ...     x, y, z = point
        ...     return 2 * x * x + 2 * y * y + 3 * z * z
        >>> f = df.Field(mesh, dim=1, value=value_fun)
        >>> laplace = Math(m=f.array, dim=1, dx=2, dy=2, dz=2).laplace()
        
        Check the laplace value
        
        >>> average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> assert average == 14
        
        2. Compute Laplacian of a vector field.For a field we
        choose :math:`f(x, y, z) = (2x^{2}, 2y^{2}, 3z^{2}) `.
        Accordingly, we expect the Laplacian to be a constant vector field
        :math:`\\nabla f = (4, 4, 6)`.
        Note that we need to ignore the value of the boundary
 
        >>> import discretisedfield as df
        >>> mesh = df.Mesh(p1=(0, 0, 0), p2=(10, 10, 10), cell=(2, 2, 2))
        >>> def value_fun(point):
        ...     x, y, z = point
        ...     return (2 * x * x, 2 * y * y, 3 * z * z)
        >>> f = df.Field(mesh, dim=3, value=value_fun)
        >>> laplace = Math(m=f.array, dim=3, dx=2, dy=2, dz=2).laplace()   
        
        Check the laplace value
        
        >>> average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> assert np.allclose(average, (4, 4, 6))    
        """
        laplace_array = self.derivative(direction="x", n=2,
                                        bc="neumann", bc_input=0) + \
            self.derivative(direction="y", n=2, bc="neumann", bc_input=0) + \
            self.derivative(direction="z", n=2, bc="neumann", bc_input=0)
        return laplace_array

    def curl(self):
        """
        The curl function takes in a vector field and
        returns the curl of that vector field
        
        .. math::
            \\nabla \\times \\mathbf{v} = \\left(\\frac{\\partial
            v_{z}}{\\partial y} - \\frac{\\partial v_{y}}{\\partial z},
            \\frac{\\partial v_{x}}{\\partial z} - \\frac{\\partial
            v_{z}}{\\partial x}, \\frac{\\partial v_{y}}{\\partial x} -
            \\frac{\\partial v_{x}}{\\partial y},\\right)
        
        Returns
        -------
        The curl of the vector field
        
        Example
        -------
        1. Compute curl of a vector field.For a field we
        choose :math:`f(x, y, z) = (x + y + z, 2x + 2y + 2z, 4y)`.
        Accordingly, we expect the curl to be a constant vector field
        .. math:: `\\nabla f = (2, 1, 1)`.
        Note that we need to ignore the value of the boundary
        
        >>> mesh = df.Mesh(p1=(0, 0, 0), p2=(10, 10, 10), cell=(2, 2, 2))
        >>> def value_fun(point):
        ...    x, y, z = point
        ...    return (x+y+z, 2*x+2*y+2*z, 4*y)
        >>> f = df.Field(mesh, dim=3, value=value_fun)
        >>> math = Math(m=f.array, dim=3, dx=2, dy=2, dz=2)
        >>> curl = math.curl()
        
        Check the curl value
        
        >>> average = curl[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        >>> assert np.allclose(average, (2,1,1))  
        """
        padding = self.pad(bc="dirichlet", bc_input=0)
        padding_shape = (padding.shape[0], padding.shape[1],
                         padding.shape[2], 1)
        Fx = self.__class__(padding[:, :, :, 0].reshape(padding_shape), dim=1,
                            dx=self.dx, dy=self.dy, dz=self.dz)
        Fy = self.__class__(padding[:, :, :, 1].reshape(padding_shape), dim=1,
                            dx=self.dx, dy=self.dy, dz=self.dz)
        Fz = self.__class__(padding[:, :, :, 2].reshape(padding_shape), dim=1,
                            dx=self.dx, dy=self.dy, dz=self.dz)
        result_shape = (self.m.shape[0], self.m.shape[1], self.m.shape[2])
        curl_xyz = np.zeros((self.m.shape[0], self.m.shape[1],
                            self.m.shape[2], self.dim))
        curl_xyz[:, :, :, 0] = (Fz.derivative("y", 1, None, None) -
                                Fy.derivative("z", 1, None, None)).reshape(
                                      result_shape)
        curl_xyz[:, :, :, 1] = (Fx.derivative("z", 1, None, None) -
                                Fz.derivative("x", 1, None, None)).reshape(
                                     result_shape)
        curl_xyz[:, :, :, 2] = (Fy.derivative("x", 1, None, None) -
                                Fx.derivative("y", 1, None, None)).reshape(
                                     result_shape)
        return curl_xyz
