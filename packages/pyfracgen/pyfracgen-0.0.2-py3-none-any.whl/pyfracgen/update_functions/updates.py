from numpy import conj
from cmath import sin, cos, exp
from numba import jit


@jit
def power(z, c, n=2):
    return z**n + c


@jit
def conj_power(z, c, n=2):
    return conj(z)**n + c


@jit
def cosine(z, c):
    return c*cos(z)


@jit
def sine(z, c):
    return c*sin(z)


@jit
def exponential(z, c):
    return c*exp(z)


@jit
def magnetic_1(z, c):

    t0 = (z*z+c-1) / (2*z+c-2)
    t1 = (z*z+c-1) / (2*z+c-2)

    return t0 * t1


@jit
def magnetic_2(z, c):

    t0 = ((z*z*z * 3*(c-1)*z + (c-1)*(c-2)) /
          (3*z*z + 3*(c-2)*z + (c-1)*(c-2) + 1))
    t1 = ((z*z*z * 3*(c-1)*z + (c-1)*(c-2)) /
          (3*z*z + 3*(c-2)*z + (c-1)*(c-2) + 1))

    return t0 * t1
