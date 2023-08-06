'''
Author: acse-xy721 xy721@ic.ac.uk
Date: 2022-07-19 13:32:04
LastEditors: acse-xy721 xy721@ic.ac.uk
LastEditTime: 2022-08-08 15:47:09
FilePath: /YXYIPR/test/testall.py
'''
import pytest
import micromagneticmodel as mm
import oommfc as oc
import discretisedfield as df
import numpy as np
from meanfield.Math import Math
from meanfield.Exchange import Exchange
from meanfield.Zeeman import Zeeman
from meanfield.DMI import DMI
import sys
sys.path.append("..")


@pytest.fixture(scope='module')
def getdfFeild(L=50e-9, dx=10e-9, dy=10e-9, dz=10e-9, dim=3, Ms=2):
    """
    It creates a random magnetization field
    with a given mesh size and magnetization
    param L: int
        length of the continuous magnetization field
    param dx: int
        the size of the discrete magnetization field in the x direction
    param dy: int
        the size of the discrete magnetization field in the y direction
    param dz: int
        the size of the discrete magnetization field in the z direction
    param dim: int
        dimension of the field (3 for a vector field)
    param Ms: int
        Saturation magnetization
    return:
        A field object.
    """
    region = df.Region(p1=(0, 0, 0), p2=(L, L, L))
    mesh = df.Mesh(region=region, cell=(dx, dy, dz))

    def value_fun(point):
        """
        It generates a random vector of length 3, normalizes it,
        and returns the first three elements of the normalized vector
        return:
            A tuple of 3 floats.
        """
        vec = np.random.randn(3)
        unit_vec = vec / np.linalg.norm(vec)
        return (unit_vec[0], unit_vec[1], unit_vec[2])
    m = df.Field(mesh, dim=dim, value=value_fun, norm=Ms)
    return m


@pytest.fixture(scope='module')
def getOommfSystem(getdfFeild):
    """
    `getOommfSystem` is a fixture that returns a `mm.System` object
    with a `m` attribute that is a`mm.Field` object
    with a `data` attribute that is a `numpy.ndarray` object
    with a `shape` attribute that is a `tuple` object
    with a `len` attribute that is an `int` object
    with a value of `3`
    param getdfFeild: object
        This is the object that contains the field data
    return:
        The system object is being returned.
    """
    system = mm.System(name='test_effective')
    system.m = getdfFeild
    return system


class TestEffectiveFeild:
    @pytest.mark.parametrize(
        ' dx, dy, dz, A, Ms, dim',
        [
            (10e-9, 10e-9, 10e-9, 1, 2, 3)
        ]
    )
    def testExchange(self, getdfFeild, getOommfSystem, dx, dy, dz, A, Ms, dim):
        """
        `testExchange` is a function that takes in a `getdfFeild` object,
        a `getOommfSystem` object, and a set of parameters (`dx, dy, dz,
        A, Ms, dim`) and tests whether the effective field computed by OOMMF
        and the effective field computed by the math module are the same.
        getdfFeild:
            This is the function that returns the field from the OOMMF system
        getOommfSystem:
            This is the OOMMF system that we are testing
        dx:
            cell size in x direction
        dy:
            the y-dimension of the mesh
        dz:
            the thickness of the mesh
        A:
            Exchange constant
        Ms:
            Saturation magnetization
        dim:
            dimension of the mesh
        """
        getOommfSystem.energy = (mm.Exchange(A=A))
        oommf_eff_ex = oc.compute(
            getOommfSystem.energy.exchange.effective_field,
            getOommfSystem).array
        math = Math(getdfFeild.value/Ms, dim, dx, dy, dz)
        math_eff_ex = Exchange(A=A, miu0=mm.consts.mu0,
                               Ms=Ms).effective_field(math)
        assert np.allclose(oommf_eff_ex, math_eff_ex)

    @pytest.mark.parametrize(
        ' dx, dy, dz, dim, H, Ms',
        [
            (10e-9, 10e-9, 10e-9, 3, (3, 2, 1), 2)
        ]
    )
    def testZeeman(self, getdfFeild, getOommfSystem, dx, dy, dz, dim, H, Ms):
        """
        `testZeeman` is a function that takes in a `getdfFeild` object,
        a `getOommfSystem` object, and a set of parameters(`dx, dy,
        dz, dim, H`)and tests whether the effective field computed by OOMMF
        and the effective field computed by the math module are the same.
        getdfFeild:
            This is the function that returns the dataframe of the field
        getOommfSystem:
            This is the OOMMF system that we are testing
        dx:
            the x-dimension of the mesh
        dy:
            y-dimension of the mesh
        dz:
            the z-dimension of the mesh
        dim:
            dimension of the system
        H:
            The external magnetic field in A/m
        """
        getOommfSystem.energy = (mm.Zeeman(H=H))
        oommf_eff_zm = oc.compute(
            getOommfSystem.energy.zeeman.effective_field, getOommfSystem).array
        math = Math(getdfFeild.value/Ms, dim, dx, dy, dz)
        math_eff_zm = Zeeman(H).effective_field(math)
        assert np.allclose(oommf_eff_zm, math_eff_zm)

    @pytest.mark.parametrize(
        ' dx, dy, dz, dim, D , A, Ms',
        [
            (10e-9, 10e-9, 10e-9, 3, 2, 2, 2)
        ]
    )
    def testDMI(self, getdfFeild, getOommfSystem, dx, dy, dz, dim, D, A, Ms):
        getOommfSystem.energy = (mm.DMI(D=D, crystalclass='T'))
        oommf_eff_dmi = oc.compute(
            getOommfSystem.energy.dmi.effective_field, getOommfSystem).array
        math = Math(getdfFeild.value/Ms, dim, dx, dy, dz)
        math_eff_dmi = DMI(D=D, miu0=mm.consts.mu0,
                           Ms=Ms).effective_field(math)
        assert np.allclose(oommf_eff_dmi, math_eff_dmi)


class TestMath:
    def testFirstDerivative(self):
        mesh = df.Mesh(region=df.Region(
            p1=(0, 0, 0),
            p2=(100e-9, 100e-9, 100e-9)),
            cell=(10e-9, 10e-9, 10e-9))

        def test_fun(point):
            x, y, z = point
            return 2*x + y
        fun_matrix = df.Field(mesh, dim=1, value=test_fun).array
        # my own func
        math = Math(m=fun_matrix, dim=1, dx=10e-9, dy=10e-9, dz=10e-9)
        first_Derivative_x = math.derivative(direction="x", n=1,
                                             bc="pbc", bc_input=None)
        first_Derivative_y = math.derivative(direction="y", n=1,
                                             bc="pbc", bc_input=None)
        first_Derivative_z = math.derivative(direction="z", n=1,
                                             bc="pbc", bc_input=None)
        average_x = first_Derivative_x[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_y = first_Derivative_y[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_z = first_Derivative_z[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average_x, 2)
        assert np.allclose(average_y, 1)
        assert np.allclose(average_z, 0)

    def testFirstDerivative_vectorFeild(self):
        """
        This function tests the first derivative function
        for a vector feild(dim = 3)
        """
        mesh = df.Mesh(region=df.Region(
            p1=(0, 0, 0),
            p2=(100e-9, 100e-9, 100e-9)),
            cell=(10e-9, 10e-9, 10e-9))

        def test_fun(point):
            x, y, z = point
            return (2*x + 1, 3*x, y+z)
        fun_matrix = df.Field(mesh, dim=3, value=test_fun).array
        # my own func
        math = Math(m=fun_matrix, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        first_Derivative_x = math.derivative(direction="x", n=1,
                                             bc="pbc", bc_input=None)
        first_Derivative_y = math.derivative(direction="y", n=1,
                                             bc="pbc", bc_input=None)
        first_Derivative_z = math.derivative(direction="z", n=1,
                                             bc="pbc", bc_input=None)
        average_x = first_Derivative_x[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_y = first_Derivative_y[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_z = first_Derivative_z[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average_x, (2, 3, 0))
        assert np.allclose(average_y, (0, 0, 1))
        assert np.allclose(average_z, (0, 0, 1))

    def testSecondDerivative(self):
        mesh = df.Mesh(region=df.Region(
            p1=(0, 0, 0),
            p2=(100e-9, 100e-9, 100e-9)),
            cell=(10e-9, 10e-9, 10e-9))

        def test_fun(point):
            x, y, z = point
            return x**2+y
        fun_matrix = df.Field(mesh, dim=1, value=test_fun).array
        math = Math(m=fun_matrix, dim=1, dx=10e-9, dy=10e-9, dz=10e-9)
        second_Derivative_x = math.derivative(direction="x", n=2,
                                              bc="pbc", bc_input=None)
        second_Derivative_y = math.derivative(direction="y", n=2,
                                              bc="pbc", bc_input=None)
        second_Derivative_z = math.derivative(direction="z", n=2,
                                              bc="pbc", bc_input=None)
        average_x = second_Derivative_x[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_y = second_Derivative_y[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_z = second_Derivative_z[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average_x, 2)
        assert np.allclose(average_y, 0)
        assert np.allclose(average_z, 0)

    def testSecondDerivative_vectorFeild(self):
        """
        This function tests the first derivative function
        for a vector feild(dim = 3)
        """
        mesh = df.Mesh(region=df.Region(
            p1=(0, 0, 0),
            p2=(100e-9, 100e-9, 100e-9)),
            cell=(10e-9, 10e-9, 10e-9))

        def test_fun(point):
            x, y, z = point
            return (z**2, 3*x+1, y**2)
        fun_matrix = df.Field(mesh, dim=3, value=test_fun).array
        # my own func
        math = Math(m=fun_matrix, dim=3, dx=10e-9, dy=10e-9, dz=10e-9)
        second_Derivative_x = math.derivative(direction="x", n=2,
                                              bc="pbc", bc_input=None)
        second_Derivative_y = math.derivative(direction="y", n=2,
                                              bc="pbc", bc_input=None)
        second_Derivative_z = math.derivative(direction="z", n=2,
                                              bc="pbc", bc_input=None)
        average_x = second_Derivative_x[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_y = second_Derivative_y[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        average_z = second_Derivative_z[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average_x, (0, 0, 0))
        assert np.allclose(average_y, (0, 0, 2))
        assert np.allclose(average_z, (2, 0, 0))

    def testLaplace(self):
        mesh = df.Mesh(p1=(0, 0, 0), p2=(10, 10, 10), cell=(2, 2, 2))
        f = df.Field(mesh, dim=3, value=(0, 0, 0))
        math = Math(m=f.array, dim=3, dx=2, dy=2, dz=2)
        laplace = math.laplace()
        average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average, (0, 0, 0))

        def value_fun(point):
            x, y, z = point
            return x + y + z
        f = df.Field(mesh, dim=1, value=value_fun)
        laplace = Math(m=f.array, dim=1, dx=2, dy=2, dz=2).laplace()
        average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert average == 0

        def value_fun(point):
            x, y, z = point
            return 2 * x * x + 2 * y * y + 3 * z * z
        f = df.Field(mesh, dim=1, value=value_fun)
        laplace = Math(m=f.array, dim=1, dx=2, dy=2, dz=2).laplace()
        average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert average == 14

        def value_fun(point):
            x, y, z = point
            return (2 * x * x, 2 * y * y, 3 * z * z)
        f = df.Field(mesh, dim=3, value=value_fun)
        laplace = Math(m=f.array, dim=3, dx=2, dy=2, dz=2).laplace()
        average = laplace[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average, (4, 4, 6))

    def testCurl(self):
        mesh = df.Mesh(p1=(0, 0, 0), p2=(10, 10, 10), cell=(2, 2, 2))
        f = df.Field(mesh, dim=3, value=(0, 0, 0))
        math = Math(m=f.array, dim=3, dx=2, dy=2, dz=2)
        curl = math.curl()
        average = curl[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average, (0, 0, 0))

        def value_fun(point):
            x, y, z = point
            return (x, y, z)
        f = df.Field(mesh, dim=3, value=value_fun)
        math = Math(m=f.array, dim=3, dx=2, dy=2, dz=2)
        curl = math.curl()
        average = curl[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average, (0, 0, 0))
        
        def value_fun(point):
            x, y, z = point
            return (x+y+z, 2*x+2*y+2*z, 4*y)
        f = df.Field(mesh, dim=3, value=value_fun)
        math = Math(m=f.array, dim=3, dx=2, dy=2, dz=2)
        curl = math.curl()
        average = curl[1:-1, 1:-1, 1:-1].mean(axis=(0, 1, 2))
        assert np.allclose(average, (2,1,1))
